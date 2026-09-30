#!/usr/bin/env python3
"""M8: fixed memory-horizon sweep for delayed supervised credit assignment."""
from __future__ import annotations
import csv, hashlib, json, platform
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = REPO_ROOT / "data/results/M8_TRACE_HORIZON_FRONTIER/reproduction"
MASTER_SEED = 20260930
N_INPUT, N_FEATURES, N_OUTPUT = 32, 64, 4
N_TRAIN, N_TEST, N_SEEDS = 3000, 1000, 30
RHOS, DELAYS, HORIZONS = (0.0, 0.5, 0.9), (4, 16, 64), (1, 4, 16, 64)
GAMMA, LR, BOOTSTRAPS = 0.98, 0.01, 20000

def stream(rng, rho, n):
    x = np.empty((n, N_INPUT)); x[0] = rng.normal(size=N_INPUT)
    scale = np.sqrt(1-rho*rho)
    for t in range(1, n): x[t] = rho*x[t-1] + scale*rng.normal(size=N_INPUT)
    return x

def make_task(rho, seed):
    base = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, seed, 101]))
    projection = base.normal(size=(N_INPUT, N_FEATURES))/np.sqrt(N_INPUT)
    teacher = base.normal(size=(N_FEATURES, N_OUTPUT))/np.sqrt(N_FEATURES)
    rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, int(rho*10), seed, 707]))
    xtr, xte = stream(rng, rho, N_TRAIN), stream(rng, rho, N_TEST)
    ftr, fte = np.tanh(xtr@projection), np.tanh(xte@projection)
    ftr /= np.maximum(np.linalg.norm(ftr, axis=1, keepdims=True), 1e-12)
    fte /= np.maximum(np.linalg.norm(fte, axis=1, keepdims=True), 1e-12)
    return ftr, np.argmax(ftr@teacher, axis=1), fte, np.argmax(fte@teacher, axis=1)

def softmax(z):
    e = np.exp(z-np.max(z)); return e/e.sum()

def train(f, y, ft, yt, delay):
    arms = [f"HORIZON_{h}" for h in HORIZONS] + ["EXACT_REPLAY"]
    w = {a: np.zeros((N_FEATURES, N_OUTPUT)) for a in arms}
    pred = {a: [] for a in arms}
    buffers = {h: [] for h in HORIZONS if h > 1}
    for t in range(N_TRAIN+delay):
        has_x = t < N_TRAIN
        x = f[t] if has_x else np.zeros(N_FEATURES)
        if has_x:
            for h, buf in buffers.items():
                buf.append((t, x.copy()))
                if len(buf) > h: buf.pop(0)
            for a in arms: pred[a].append(softmax(x@w[a]))
        j = t-delay
        if not 0 <= j < N_TRAIN: continue
        target = np.zeros(N_OUTPUT); target[y[j]] = 1
        err = {a: target-pred[a][j] for a in arms}
        for h in HORIZONS:
            a = f"HORIZON_{h}"
            if h == 1:
                elig = x
            else:
                hist = buffers[h]
                elig = sum((GAMMA**(t-index))*vec for index,vec in hist) if hist else np.zeros(N_FEATURES)
            update = elig/max(np.linalg.norm(elig), 1e-12)
            w[a] += LR*np.outer(update, err[a])
        a = "EXACT_REPLAY"
        w[a] += LR*np.outer(f[j], err[a])
    if any(not np.isfinite(v).all() for v in w.values()):
        raise FloatingPointError("non-finite model weights")
    return {a: float(np.mean(np.argmax(ft@w[a], axis=1)==yt)) for a in arms}

def ci(v, seed):
    rng=np.random.default_rng(seed); v=np.asarray(v); ix=rng.integers(0,len(v),(BOOTSTRAPS,len(v)))
    m=v[ix].mean(axis=1); return [float(np.quantile(m,.025)),float(np.quantile(m,.975))]

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    rows=[]
    for rho in RHOS:
        for seed in range(N_SEEDS):
            f,y,ft,yt=make_task(rho,seed)
            for d in DELAYS:
                for arm,score in train(f,y,ft,yt,d).items():
                    h=int(arm.split('_')[1]) if arm.startswith('HORIZON_') else None
                    rows.append({'rho':rho,'seed':seed,'delay':d,'arm':arm,'horizon':h,'accuracy':score,
                                 'history_float_values':0 if h==1 else (h*N_FEATURES if h else d*N_FEATURES),
                                 'n_train':N_TRAIN,'n_test':N_TEST})
    path=OUT/'task_metrics.csv'
    with path.open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    lookup={(r['rho'],r['seed'],r['delay'],r['arm']):r['accuracy'] for r in rows}
    per_seed=[]; cells=[]
    for seed in range(N_SEEDS):
        diffs=[]
        for rho in RHOS:
            for d in DELAYS:
                diffs.append(lookup[(rho,seed,d,'HORIZON_64')]-lookup[(rho,seed,d,'HORIZON_1')])
        per_seed.append(float(np.mean(diffs)))
    for rho in RHOS:
        for d in DELAYS:
            for h in HORIZONS:
                v=np.array([lookup[(rho,s,d,f'HORIZON_{h}')]-lookup[(rho,s,d,'HORIZON_1')] for s in range(N_SEEDS)])
                replay=np.array([lookup[(rho,s,d,f'HORIZON_{h}')]-lookup[(rho,s,d,'EXACT_REPLAY')] for s in range(N_SEEDS)])
                cells.append({'rho':rho,'delay':d,'horizon':h,'accuracy_gain_vs_h1':float(v.mean()),
                    'seed_bootstrap_95ci':ci(v,MASTER_SEED+int(rho*100)+d+h),
                    'accuracy_difference_vs_exact_replay':float(replay.mean()),'stored_float_values':h*N_FEATURES})
    result={'experiment':'M8_TRACE_HORIZON_FRONTIER','status':'POST_RESULT_EXPLORATORY',
      'primary':{'estimand':'accuracy(HORIZON_64)-accuracy(HORIZON_1), equally averaged across rho and delay within seed',
        'mean':float(np.mean(per_seed)),'seed_bootstrap_95ci':ci(per_seed,MASTER_SEED+8000),'positive_seed_count':int(np.sum(np.array(per_seed)>0)),'n_task_seeds':N_SEEDS},
      'cells':cells,'n_rows':len(rows),'gamma':GAMMA,'learning_rate':LR,
      'scope':'synthetic random-feature classification only; not biological validation or general AI transfer'}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    with (OUT/'primary_seed_contrasts.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=['seed','horizon64_minus_horizon1']);wr.writeheader()
        wr.writerows({'seed':s,'horizon64_minus_horizon1':v} for s,v in enumerate(per_seed))
    manifest={'experiment':'M8_TRACE_HORIZON_FRONTIER','seed':MASTER_SEED,'n_seeds':N_SEEDS,'rho':RHOS,'delays':DELAYS,'horizons':HORIZONS,
      'n_train':N_TRAIN,'n_test':N_TEST,'gamma':GAMMA,'learning_rate':LR,'python':platform.python_version(),'numpy':np.__version__,'rows':len(rows),'sha256':{}}
    tracked=[REPO_ROOT/'summery/M8_TRACE_HORIZON_FRONTIER/EXPERIMENT_CONTRACT.md',ROOT/'run_experiment.py',path,OUT/'summary.json',OUT/'primary_seed_contrasts.csv']
    for p in tracked:
        try: label=str(p.relative_to(ROOT))
        except ValueError: label=str(p.relative_to(REPO_ROOT))
        manifest['sha256'][label]=hashlib.sha256(p.read_bytes()).hexdigest()
    (OUT/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'primary':result['primary'],'cells':len(cells)},indent=2))

if __name__=='__main__': main()
