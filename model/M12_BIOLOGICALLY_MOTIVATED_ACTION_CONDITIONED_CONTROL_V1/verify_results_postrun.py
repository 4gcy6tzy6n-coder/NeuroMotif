#!/usr/bin/env python3
"""Post-run corrective checker for M12; preserves the frozen pre-run verifier."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
import numpy as np
from scipy.stats import ttest_1samp

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/results/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1'
CONTRACT=ROOT/'summery/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/CONTRACT.md'
AMENDMENT=ROOT/'summery/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/AMENDMENT_PRE_RUN_01.md'
RUNNER=Path(__file__).with_name('run_experiment.py')
FROZEN_VERIFIER=Path(__file__).with_name('verify_results.py')
SEEDS=list(range(812000,812040))
ARMS=['MOTOR_GATED_RNN','GENERIC_GRU','MOTOR_ZERO_ABLATION','MOTOR_PERMUTED_ABLATION','KNOWN_GENERATOR_KALMAN_FIXED_GAIN','MEMORYLESS_REACTIVE']
N_TEST=128

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()

def read_csv(path):
    with open(path,newline='') as f:return list(csv.DictReader(f))

def boot(x,rng,n=20000):
    x=np.asarray(x,float); samp=np.empty(n)
    for i in range(n):samp[i]=np.mean(x[rng.integers(0,len(x),size=len(x))])
    return [float(np.quantile(samp,.025)),float(np.quantile(samp,.975))]

def close(a,b,tol=1e-10):
    return bool(abs(float(a)-float(b)) <= tol*max(1.0,abs(float(a)),abs(float(b))))

def main():
    summary=json.loads((OUT/'SUMMARY.json').read_text())
    episode=read_csv(OUT/'episode_metrics.csv'); per_seed=read_csv(OUT/'per_seed_summary.csv'); train=read_csv(OUT/'training_log.csv')
    manifest=json.loads((OUT/'MANIFEST.json').read_text()); checks={}
    checks['summary_id']=summary.get('experiment_id')=='M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1'
    checks['contract_hash_matches']=summary.get('contract_sha256')==sha(CONTRACT)==manifest['inputs']['contract_sha256']
    checks['amendment_hash_matches']=summary.get('amendment_sha256')==sha(AMENDMENT)==manifest['inputs']['amendment_sha256']
    checks['runner_hash_matches']=manifest['inputs']['runner_sha256']==sha(RUNNER)
    checks['frozen_verifier_hash_matches']=manifest['inputs']['verifier_sha256']==sha(FROZEN_VERIFIER)
    checks['source_hash_chain_matches']=(summary['runner_sha256']==sha(RUNNER)==manifest['inputs']['runner_sha256'] and summary['verifier_sha256']==sha(FROZEN_VERIFIER)==manifest['inputs']['verifier_sha256'])
    pre=json.loads((OUT/'PREFLIGHT.json').read_text()); cfg=OUT/'resolved_config.json'
    checks['preflight_hash_matches']=summary['preflight_sha256']==sha(OUT/'PREFLIGHT.json')==manifest['inputs']['preflight_sha256']
    checks['config_hash_matches']=summary['resolved_config_sha256']==sha(cfg)==manifest['inputs']['resolved_config_sha256']==pre['resolved_config_sha256']
    checks['preflight_sources_match']=pre['runner_sha256']==sha(RUNNER) and pre['verifier_sha256']==sha(FROZEN_VERIFIER) and pre['contract_sha256']==sha(CONTRACT) and pre['pre_run_amendment_sha256']==sha(AMENDMENT)
    checks['manifest_outputs_match']=all(sha(OUT/name)==expected for name,expected in manifest['outputs'].items())
    impl_pre=json.loads((OUT/'IMPLEMENTATION_PREFLIGHT.json').read_text())
    checks['implementation_preflight_passed']=impl_pre['status']=='PASS' and impl_pre['outcomes_generated'] is False and all(impl_pre[k] for k in ['contract_hash_match','amendment_hash_match','runner_hash_match','verifier_hash_match','resolved_config_hash_match'])
    checks['implementation_preflight_hash_matches']=summary['implementation_preflight_sha256']==sha(OUT/'IMPLEMENTATION_PREFLIGHT.json')
    keys={(int(r['seed']),int(r['episode']),r['arm']) for r in episode}; expected={(s,e,a) for s in SEEDS for e in range(N_TEST) for a in ARMS}
    checks['episode_rows_complete_and_unique']=len(episode)==len(expected) and len(keys)==len(episode) and keys==expected
    pkeys={(int(r['seed']),r['arm']) for r in per_seed}; pexpected={(s,a) for s in SEEDS for a in ARMS}
    checks['per_seed_rows_complete_and_unique']=len(per_seed)==len(pexpected) and len(pkeys)==len(per_seed) and pkeys==pexpected
    train_keys={(int(r['seed']),r['arm'],int(r['epoch'])) for r in train}; texpected={(s,a,e) for s in SEEDS for a in ARMS[:4] for e in range(1,31)}
    checks['training_log_complete_and_unique']=len(train)==len(texpected) and len(train_keys)==len(train) and train_keys==texpected
    eagg={}
    for row in episode:eagg.setdefault((int(row['seed']),row['arm']),[]).append(float(row['normalized_tracking_mse']))
    pmap={(int(r['seed']),r['arm']):float(r['mean_normalized_tracking_mse']) for r in per_seed}
    checks['episode_to_seed_arithmetic']=all(close(np.mean(v),pmap[k]) for k,v in eagg.items())
    vals={a:np.asarray([pmap[(s,a)] for s in SEEDS]) for a in ARMS}
    checks['arm_means_match_summary']=all(close(vals[a].mean(),summary['arm_means_normalized_mse'][a]) for a in ARMS)
    primary=vals[ARMS[0]]-vals[ARMS[1]]; rng=np.random.default_rng(812999); pci=boot(primary,rng)
    checks['primary_contrast_matches']=close(primary.mean(),summary['primary']['mean_difference']) and all(close(x,y) for x,y in zip(pci,summary['primary']['ci95_percentile_seed_bootstrap']))
    sec={}; raw=[]
    for arm in ARMS[2:4]:
        d=vals[ARMS[0]]-vals[arm]; ci=boot(d,rng); p=float(ttest_1samp(d,0.0,alternative='two-sided').pvalue)
        sec[arm]=(float(d.mean()),ci,p); raw.append((arm,p))
    sortedp=sorted(raw,key=lambda z:z[1]); adj={}; running=0.
    for i,(arm,p) in enumerate(sortedp):running=max(running,(len(sortedp)-i)*p); adj[arm]=min(1.,running)
    secondary_ok=True
    for arm,(mean,ci,p) in sec.items():
        s=summary['secondary'][arm]
        secondary_ok &= close(mean,s['mean_difference']) and all(close(x,y) for x,y in zip(ci,s['ci95_percentile_seed_bootstrap'])) and close(p,s['paired_t_p_two_sided']) and close(adj[arm],s['holm_adjusted_p'])
    checks['secondary_contrasts_match']=bool(secondary_ok)
    refs=(vals['MEMORYLESS_REACTIVE'].mean()-vals['KNOWN_GENERATOR_KALMAN_FIXED_GAIN'].mean())/vals['MEMORYLESS_REACTIVE'].mean()
    recomputed_failures={a:sum(int(r['failed']) for r in episode if r['arm']==a) for a in ARMS}
    ref_fail=max(recomputed_failures[a]/(len(SEEDS)*N_TEST) for a in ARMS[4:])
    checks['task_viability_recomputed']=close(refs,summary['task_viability']['reference_relative_improvement_over_reactive'])
    checks['task_viability_disposition_matches']=bool(summary['task_viability']['passed'])==(refs>=0.10 and ref_fail<=0.01)
    expected_viable=refs>=0.10 and ref_fail<=0.01
    if not expected_viable: expected_status='INCONCLUSIVE_TASK_VIABILITY_FAILED'
    elif pci[1]<0 and -float(primary.mean())/float(vals['GENERIC_GRU'].mean())>=0.02: expected_status='BOUNDED_PRACTICALLY_RELEVANT_ARCHITECTURE_ADVANTAGE'
    elif pci[0]>0: expected_status='BOUNDED_ARCHITECTURE_DISADVANTAGE'
    else: expected_status='NO_PRACTICALLY_RELEVANT_ADVANTAGE_ESTABLISHED'
    checks['disposition_matches_frozen_rules']=summary['status']==expected_status
    checks['parameter_counts_match']=summary['parameter_counts']=={'MOTOR_GATED_RNN':232,'GENERIC_GRU':223,'MOTOR_ZERO_ABLATION':232,'MOTOR_PERMUTED_ABLATION':232}
    checks['finite_numeric_outputs']=all(np.isfinite(float(r[k])) for r in episode for k in ['mean_squared_tracking_error','normalized_tracking_mse','action_std','sign_switch_rate']) and all(np.isfinite(float(r['train_action_mse'])) for r in train)
    normvar=0.08**2/(1-0.97**2)
    checks['episode_normalization_matches']=all(close(float(r['normalized_tracking_mse']),float(r['mean_squared_tracking_error'])/normvar) for r in episode)
    checks['failure_counts_match']=recomputed_failures==summary['failure_counts']
    checks['reference_failure_rate_matches']=close(ref_fail,summary['task_viability']['reference_failure_rate_max'])
    checks={k:bool(v) for k,v in checks.items()}
    report={'experiment_id':summary['experiment_id'],'verification':'PASS' if all(checks.values()) else 'FAIL','checker':'verify_results_postrun.py','checker_sha256':sha(Path(__file__)),'frozen_verifier_sha256':sha(FROZEN_VERIFIER),'note':'Post-run corrective checker; original frozen verifier was preserved byte-for-byte.','checks':checks,'episode_rows':len(episode),'per_seed_rows':len(per_seed),'training_log_rows':len(train),'manifest_sha256':sha(OUT/'MANIFEST.json')}
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
    if not all(checks.values()):raise SystemExit(1)

if __name__=='__main__':main()
