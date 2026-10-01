#!/usr/bin/env python3
"""M12 frozen synthetic motor-state feedback transfer benchmark."""
from __future__ import annotations
import csv, hashlib, json, os, platform, sys, time
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import numpy as np
import scipy
from scipy.stats import ttest_1samp
import torch
from torch import nn
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / 'summery/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/CONTRACT.md'
AMENDMENT = ROOT / 'summery/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/AMENDMENT_PRE_RUN_01.md'
OUT = ROOT / 'data/results/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1'
SEEDS = range(812000, 812040)
T = 256
N_TRAIN = 256
N_TEST = 128
BATCH = 16
EPOCHS = 30
H = 7
PHI = 0.97
QVAR = 0.08 ** 2
NORM_VAR = QVAR / (1 - PHI ** 2)
ARMS = ['MOTOR_GATED_RNN', 'GENERIC_GRU', 'MOTOR_ZERO_ABLATION', 'MOTOR_PERMUTED_ABLATION']


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


class MotorGatedRNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.carry = nn.Linear(9, 7)
        self.sensory = nn.Linear(9, 7)
        self.wx = nn.Parameter(torch.empty(7, 4))
        self.wh = nn.Parameter(torch.empty(7, 7))
        self.bx = nn.Parameter(torch.zeros(7))
        self.readout = nn.Linear(7, 1)
        nn.init.xavier_uniform_(self.wx)
        nn.init.orthogonal_(self.wh)

    def step(self, x, h):
        motor = x[:, 2:3]
        kappa = x[:, 3:4]
        gate_input = torch.cat((h, motor, kappa), dim=1)
        a = torch.sigmoid(self.carry(gate_input))
        g = torch.sigmoid(self.sensory(gate_input))
        c = torch.tanh(F.linear(x, self.wx) + F.linear(h, self.wh, self.bx))
        h = a * h + (1.0 - a) * (g * c)
        action = 0.25 * torch.tanh(self.readout(h))
        return action, h

    def sequence(self, x):
        h = torch.zeros((x.shape[0], 7), dtype=x.dtype, device=x.device)
        ys = []
        for t in range(x.shape[1]):
            y, h = self.step(x[:, t, :], h)
            ys.append(y)
        return torch.stack(ys, dim=1)


class GenericGRU(nn.Module):
    def __init__(self):
        super().__init__()
        self.cell = nn.GRUCell(4, 6)
        self.readout = nn.Linear(6, 1)

    def step(self, x, h):
        h = self.cell(x, h)
        action = 0.25 * torch.tanh(self.readout(h))
        return action, h

    def sequence(self, x):
        h = torch.zeros((x.shape[0], 6), dtype=x.dtype, device=x.device)
        ys = []
        for t in range(x.shape[1]):
            y, h = self.step(x[:, t, :], h)
            ys.append(y)
        return torch.stack(ys, dim=1)


def nparams(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def generate_demo(seed: int):
    rng = np.random.default_rng(np.random.SeedSequence([seed, 1]))
    q = np.empty((N_TRAIN, T), dtype=np.float32)
    q[:, 0] = rng.normal(0, np.sqrt(1/3), size=N_TRAIN)
    innovations = rng.normal(0, np.sqrt(QVAR), size=(N_TRAIN, T-1))
    for t in range(1, T):
        q[:, t] = PHI*q[:, t-1] + innovations[:, t-1]
    kappa = rng.uniform(0.25, 0.75, size=N_TRAIN).astype(np.float32)
    p = rng.uniform(-1, 1, size=N_TRAIN).astype(np.float32)
    uprev = np.zeros(N_TRAIN, dtype=np.float32)
    mu = np.zeros(N_TRAIN, dtype=np.float64)
    var = np.full(N_TRAIN, 1/3, dtype=np.float64)
    xs = np.empty((N_TRAIN, T, 4), dtype=np.float32)
    actions = np.empty((N_TRAIN, T, 1), dtype=np.float32)
    for t in range(T):
        sigma = 0.05 + kappa*np.abs(uprev)
        y = q[:, t] - p + rng.normal(size=N_TRAIN).astype(np.float32)*sigma
        if t > 0:
            mu *= PHI
            var = PHI**2 * var + QVAR
        r = sigma.astype(np.float64)**2
        gain = var/(var+r)
        z = y+p
        mu += gain*(z-mu)
        var *= (1-gain)
        u = np.clip(0.7*(mu-p), -0.25, 0.25).astype(np.float32)
        xs[:, t, :] = np.stack((y, p, uprev, kappa), axis=1)
        actions[:, t, 0] = u
        p = p+u
        uprev = u
    return xs, actions


def train_arm(arm, x_np, y_np, seed, orders, perm_rng):
    arm_id = ARMS.index(arm)
    init_seed = int(np.random.SeedSequence([seed, 3, arm_id]).generate_state(1)[0])
    torch.manual_seed(init_seed)
    model = MotorGatedRNN() if arm != 'GENERIC_GRU' else GenericGRU()
    model.train()
    opt = torch.optim.Adam(model.parameters(), lr=0.003, betas=(0.9, 0.999), eps=1e-8, weight_decay=0)
    X = torch.from_numpy(x_np)
    Y = torch.from_numpy(y_np)
    logs = []
    for epoch in range(EPOCHS):
        losses = []
        for order in orders[epoch]:
            xb = X[order].clone()
            yb = Y[order]
            if arm == 'MOTOR_ZERO_ABLATION':
                xb[:, :, 2] = 0.0
            elif arm == 'MOTOR_PERMUTED_ABLATION':
                for t in range(T):
                    perm = perm_rng.permutation(len(order))
                    xb[:, t, 2] = xb[perm, t, 2].clone()
            pred = model.sequence(xb)
            loss = F.mse_loss(pred, yb)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            losses.append(float(loss.detach()))
        logs.append({'seed': seed, 'arm': arm, 'epoch': epoch+1, 'train_action_mse': float(np.mean(losses))})
    model.eval()
    return model, logs


def test_paths(seed):
    rng = np.random.default_rng(np.random.SeedSequence([seed, 2]))
    q = np.empty((N_TEST, T), dtype=np.float32)
    q[:, 0] = rng.normal(0, np.sqrt(1/3), size=N_TEST)
    innovations = rng.normal(0, np.sqrt(QVAR), size=(N_TEST, T-1))
    for t in range(1, T):
        q[:, t] = PHI*q[:, t-1] + innovations[:, t-1]
    znoise = rng.normal(size=(N_TEST, T)).astype(np.float32)
    kappas = rng.uniform(0.25, 0.75, size=N_TEST).astype(np.float32)
    p0 = rng.uniform(-1, 1, size=N_TEST).astype(np.float32)
    return q, znoise, kappas, p0


def rollout_model(model, arm, q, znoise, kappas, p0, perm_rng):
    b = len(p0)
    p = p0.copy()
    uprev = np.zeros(b, dtype=np.float32)
    hsize = 6 if isinstance(model, GenericGRU) else 7
    h = torch.zeros((b, hsize), dtype=torch.float32)
    errs = np.empty((b, T), dtype=np.float64)
    acts = np.empty((b, T), dtype=np.float32)
    model.eval()
    with torch.no_grad():
        for t in range(T):
            sigma = 0.05 + kappas*np.abs(uprev)
            y = q[:, t]-p+sigma*znoise[:, t]
            motor_in = uprev.copy()
            if arm == 'MOTOR_ZERO_ABLATION':
                motor_in.fill(0)
            elif arm == 'MOTOR_PERMUTED_ABLATION':
                motor_in = motor_in[perm_rng.permutation(b)]
            x = torch.from_numpy(np.stack((y, p, motor_in, kappas), axis=1).astype(np.float32))
            u, h = model.step(x, h)
            u = u.squeeze(1).cpu().numpy().astype(np.float32)
            errs[:, t] = (q[:, t]-p)**2
            acts[:, t] = u
            p = p+u
            uprev = u
    return errs, acts


def rollout_reference(kind, q, znoise, kappas, p0):
    b = len(p0)
    p = p0.copy()
    uprev = np.zeros(b, dtype=np.float32)
    mu = np.zeros(b, dtype=np.float64)
    var = np.full(b, 1/3, dtype=np.float64)
    errs = np.empty((b, T), dtype=np.float64)
    acts = np.empty((b, T), dtype=np.float32)
    for t in range(T):
        sigma = 0.05 + kappas*np.abs(uprev)
        y = q[:, t]-p+sigma*znoise[:, t]
        if kind == 'KNOWN_GENERATOR_KALMAN_FIXED_GAIN':
            if t > 0:
                mu *= PHI
                var = PHI**2*var+QVAR
            gain = var/(var+sigma.astype(np.float64)**2)
            mu += gain*(y+p-mu)
            estimate = mu
        else:
            estimate = y+p
        u = np.clip(0.7*(estimate-p), -0.25, 0.25).astype(np.float32)
        errs[:, t] = (q[:, t]-p)**2
        acts[:, t] = u
        p = p+u
        uprev = u
    return errs, acts


def bootstrap_mean(x, rng, n=20000):
    x = np.asarray(x, dtype=float)
    samples = np.empty(n, dtype=float)
    for i in range(n):
        samples[i] = np.mean(x[rng.integers(0, len(x), size=len(x))])
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def write_csv(path, rows, fields):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def main():
    if sys.argv[1:] == ['--preflight-only']:
        ng, nr = nparams(MotorGatedRNN()), nparams(GenericGRU())
        pre = json.loads((OUT/'PREFLIGHT.json').read_text())
        checks = {'motor_gated_params': ng, 'generic_gru_params': nr, 'relative_parameter_difference': abs(ng-nr)/nr,
                  'contract_sha256_match': pre['contract_sha256'] == sha256(CONTRACT),
                  'amendment_sha256_match': pre['pre_run_amendment_sha256'] == sha256(AMENDMENT),
                  'runner_sha256_match': pre.get('runner_sha256') == sha256(Path(__file__)),
                  'verifier_sha256_match': pre.get('verifier_sha256') == sha256(Path(__file__).with_name('verify_results.py')),
                  'resolved_config_sha256_match': pre.get('resolved_config_sha256') == sha256(OUT/'resolved_config.json')}
        checks['pass'] = ng == 232 and nr == 223 and checks['relative_parameter_difference'] <= 0.05 and checks['contract_sha256_match'] and checks['amendment_sha256_match'] and checks['runner_sha256_match'] and checks['verifier_sha256_match'] and checks['resolved_config_sha256_match']
        print(json.dumps(checks, indent=2))
        if not checks['pass']:
            raise SystemExit(2)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT/'SUMMARY.json').exists():
        raise SystemExit('Refusing to overwrite existing M12 outcomes.')
    if nparams(MotorGatedRNN()) != 232 or nparams(GenericGRU()) != 223:
        raise SystemExit('Parameter-count gate failed before training.')
    if abs(232-223)/223 > 0.05:
        raise SystemExit('Parameter-match tolerance failed before training.')
    contract_hash, amendment_hash = sha256(CONTRACT), sha256(AMENDMENT)
    pre_path = OUT/'PREFLIGHT.json'
    config_path = OUT/'resolved_config.json'
    pre = json.loads(pre_path.read_text())
    config = json.loads(config_path.read_text())
    checks = {
        'contract': pre['contract_sha256'] == contract_hash,
        'amendment': pre['pre_run_amendment_sha256'] == amendment_hash,
        'runner': pre['runner_sha256'] == sha256(Path(__file__)),
        'verifier': pre['verifier_sha256'] == sha256(Path(__file__).with_name('verify_results.py')),
        'config': pre['resolved_config_sha256'] == sha256(config_path),
        'seeds': config['seed_blocks'] == [812000, 812039] and config['seed_count'] == 40,
        'budget': config['train_episodes_per_seed'] == N_TRAIN and config['test_episodes_per_seed_arm'] == N_TEST and config['epochs'] == EPOCHS and config['batch_size'] == BATCH,
        'task': config['target_phi'] == PHI and config['target_process_variance'] == QVAR and config['steps_per_episode'] == T,
        'frozen_hashes': config['contract_sha256'] == pre['contract_sha256'] and config['pre_run_amendment_sha256'] == pre['pre_run_amendment_sha256'],
    }
    if not all(checks.values()):
        raise SystemExit(f'Frozen source/config preflight mismatch; no training started: {checks}')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    t0 = time.time()
    episode_rows, train_rows = [], []
    per_seed = {arm: [] for arm in ARMS + ['KNOWN_GENERATOR_KALMAN_FIXED_GAIN','MEMORYLESS_REACTIVE']}
    failure_counts = {arm: 0 for arm in per_seed}
    param_counts = {'MOTOR_GATED_RNN': nparams(MotorGatedRNN()), 'GENERIC_GRU': nparams(GenericGRU()),
                    'MOTOR_ZERO_ABLATION': nparams(MotorGatedRNN()), 'MOTOR_PERMUTED_ABLATION': nparams(MotorGatedRNN())}
    for seed in SEEDS:
        x_np, y_np = generate_demo(seed)
        order_rng = np.random.default_rng(np.random.SeedSequence([seed, 3, 999]))
        orders = []
        for _ in range(EPOCHS):
            perm = order_rng.permutation(N_TRAIN)
            orders.append([perm[i:i+BATCH] for i in range(0, N_TRAIN, BATCH)])
        perm_rng = np.random.default_rng(np.random.SeedSequence([seed, 4]))
        q, znoise, kappas, p0 = test_paths(seed)
        all_metrics = {}
        for arm in ARMS:
            model, logs = train_arm(arm, x_np, y_np, seed, orders, perm_rng)
            train_rows.extend(logs)
            e, a = rollout_model(model, arm, q, znoise, kappas, p0, perm_rng)
            all_metrics[arm] = (e, a)
            del model
        for ref in ['KNOWN_GENERATOR_KALMAN_FIXED_GAIN','MEMORYLESS_REACTIVE']:
            all_metrics[ref] = rollout_reference(ref, q, znoise, kappas, p0)
        for arm, (e, a) in all_metrics.items():
            mse = np.mean(e, axis=1)
            nmse = mse/NORM_VAR
            action_std = np.std(a, axis=1)
            signs = np.sign(a)  # NumPy sign(0)=0.
            switch = np.mean(signs[:, 1:] != signs[:, :-1], axis=1)
            previous_actions = np.concatenate((np.zeros((N_TEST, 1), dtype=np.float32), a[:, :-1]), axis=1)
            positions = p0[:, None] + np.cumsum(previous_actions, axis=1)
            abs_error = np.sqrt(e)
            sustained_large_error = np.asarray([np.convolve(row > 5.0, np.ones(10, dtype=int), mode='valid').max() >= 10 for row in abs_error])
            failed = (~np.isfinite(e).all(axis=1)) | (~np.isfinite(a).all(axis=1)) | (~np.isfinite(positions).all(axis=1)) | sustained_large_error
            failure_counts[arm] += int(failed.sum())
            per_seed[arm].append(float(np.mean(nmse)))
            for episode in range(N_TEST):
                episode_rows.append({'seed':seed,'episode':episode,'arm':arm,'mean_squared_tracking_error':float(mse[episode]),
                    'normalized_tracking_mse':float(nmse[episode]),'action_std':float(action_std[episode]),
                    'sign_switch_rate':float(switch[episode]),'failed':int(failed[episode])})
        if seed % 5 == 4:
            print(f'completed seed blocks through {seed}; elapsed_sec={time.time()-t0:.1f}', flush=True)
    per_seed_rows=[]
    for arm, values in per_seed.items():
        for seed, value in zip(SEEDS, values): per_seed_rows.append({'seed':seed,'arm':arm,'mean_normalized_tracking_mse':value})
    # All contrasts are paired on task-seed blocks.
    vals={arm:np.asarray(v) for arm,v in per_seed.items()}
    rng=np.random.default_rng(812999)
    primary=vals['MOTOR_GATED_RNN']-vals['GENERIC_GRU']
    primary_ci=bootstrap_mean(primary,rng)
    secondary={}
    sec_p=[]
    for arm in ['MOTOR_ZERO_ABLATION','MOTOR_PERMUTED_ABLATION']:
        diff=vals['MOTOR_GATED_RNN']-vals[arm]
        ci=bootstrap_mean(diff,rng)
        p=float(ttest_1samp(diff,0.0,alternative='two-sided').pvalue)
        sec_p.append((arm,p))
        secondary[arm]={'mean_difference':float(diff.mean()),'ci95_percentile_seed_bootstrap':list(ci),'paired_t_p_two_sided':p}
    sorted_p=sorted(sec_p,key=lambda x:x[1]); adj={}; running=0.0
    for rank,(arm,p) in enumerate(sorted_p):
        adjusted=min(1.0,max(running,(len(sorted_p)-rank)*p)); adj[arm]=adjusted; running=adjusted
    for arm in secondary: secondary[arm]['holm_adjusted_p']=adj[arm]
    generic_mean=float(vals['GENERIC_GRU'].mean())
    improvement=-float(primary.mean())
    relative=improvement/generic_mean if generic_mean else float('nan')
    ref_improvement=(float(vals['MEMORYLESS_REACTIVE'].mean())-float(vals['KNOWN_GENERATOR_KALMAN_FIXED_GAIN'].mean()))/float(vals['MEMORYLESS_REACTIVE'].mean())
    max_fail=max(failure_counts[a]/(len(SEEDS)*N_TEST) for a in ['KNOWN_GENERATOR_KALMAN_FIXED_GAIN','MEMORYLESS_REACTIVE'])
    viable=ref_improvement>=0.10 and max_fail<=0.01
    if not viable: status='INCONCLUSIVE_TASK_VIABILITY_FAILED'
    elif primary_ci[1] < 0 and relative >= 0.02: status='BOUNDED_PRACTICALLY_RELEVANT_ARCHITECTURE_ADVANTAGE'
    elif primary_ci[0] > 0: status='BOUNDED_ARCHITECTURE_DISADVANTAGE'
    else: status='NO_PRACTICALLY_RELEVANT_ADVANTAGE_ESTABLISHED'
    ablation_support={arm:(secondary[arm]['mean_difference']<0 and secondary[arm]['holm_adjusted_p']<0.05) for arm in secondary}
    if status=='BOUNDED_PRACTICALLY_RELEVANT_ARCHITECTURE_ADVANTAGE' and not all(ablation_support.values()):
        mechanism_specific='NOT_ESTABLISHED'
    elif status=='BOUNDED_PRACTICALLY_RELEVANT_ARCHITECTURE_ADVANTAGE': mechanism_specific='MOTOR_PATH_SUPPORTED_WITHIN_THIS_SYNTHETIC_TASK'
    else: mechanism_specific='NOT_ESTABLISHED'
    summary={'experiment_id':'M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1','classification':'ENGINEERING_ONLY',
        'status':status,'outcome_informed_at_project_level':True,'contract_sha256':contract_hash,'amendment_sha256':amendment_hash,
        'independent_unit':'paired task-seed block','seed_count':len(SEEDS),'test_episodes_per_seed_arm':N_TEST,'steps_per_episode':T,
        'parameter_counts':param_counts,'parameter_relative_difference':abs(param_counts['MOTOR_GATED_RNN']-param_counts['GENERIC_GRU'])/param_counts['GENERIC_GRU'],
        'runner_sha256':sha256(Path(__file__)),'verifier_sha256':sha256(Path(__file__).with_name('verify_results.py')),'resolved_config_sha256':sha256(config_path),'preflight_sha256':sha256(pre_path),'implementation_preflight_sha256':sha256(OUT/'IMPLEMENTATION_PREFLIGHT.json'),
        'primary':{'contrast':'MOTOR_GATED_RNN minus GENERIC_GRU','mean_difference':float(primary.mean()),'ci95_percentile_seed_bootstrap':list(primary_ci),
                   'generic_gru_mean_normalized_mse':generic_mean,'relative_error_reduction':relative,'practical_threshold':0.02},
        'secondary':secondary,'motor_path_ablation_support':ablation_support,'mechanism_specific_transfer':'NOT_BIOLOGICALLY_VALIDATED; '+mechanism_specific,
        'task_viability':{'reference_relative_improvement_over_reactive':ref_improvement,'reference_failure_rate_max':max_fail,'passed':viable},
        'arm_means_normalized_mse':{a:float(v.mean()) for a,v in vals.items()},
        'failure_counts':failure_counts,'runtime_seconds':time.time()-t0,
        'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'torch':torch.__version__,'torch_threads':torch.get_num_threads()}}
    write_csv(OUT/'episode_metrics.csv',episode_rows,['seed','episode','arm','mean_squared_tracking_error','normalized_tracking_mse','action_std','sign_switch_rate','failed'])
    write_csv(OUT/'per_seed_summary.csv',per_seed_rows,['seed','arm','mean_normalized_tracking_mse'])
    write_csv(OUT/'training_log.csv',train_rows,['seed','arm','epoch','train_action_mse'])
    (OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    output_names=['episode_metrics.csv','per_seed_summary.csv','training_log.csv','SUMMARY.json','IMPLEMENTATION_PREFLIGHT.json']
    manifest={'experiment_id':'M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1',
        'inputs':{'contract_sha256':contract_hash,'amendment_sha256':amendment_hash,'runner_sha256':sha256(Path(__file__)),
                  'verifier_sha256':sha256(Path(__file__).with_name('verify_results.py')),'preflight_sha256':sha256(pre_path),
                  'resolved_config_sha256':sha256(config_path)},
        'outputs':{name:sha256(OUT/name) for name in output_names}}
    (OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__ == '__main__': main()
