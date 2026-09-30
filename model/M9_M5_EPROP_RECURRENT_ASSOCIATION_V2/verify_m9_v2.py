#!/usr/bin/env python3
"""Independent table-level verification and recovery of M9-v2 post-run metadata."""
import csv, hashlib, json, math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/results/M9_M5_EPROP_RECURRENT_ASSOCIATION_V2"
SEEDS = list(range(200, 230)); DELAYS = (4, 16, 64)
ARMS = ("ELIGIBILITY_TRACE", "NO_TRACE", "BPTT")
BOOT_SEED = 2026093010; N_BOOT = 20_000

def ci(x):
    rng = np.random.default_rng(BOOT_SEED)
    b = np.empty(N_BOOT)
    for i in range(N_BOOT):
        b[i] = x[rng.integers(0, len(x), len(x))].mean()
    return [float(np.quantile(b, .025)), float(np.quantile(b, .975))]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    pre = json.loads((ROOT / "M9V2_PREFLIGHT.json").read_text())
    rows = list(csv.DictReader((OUT / "M9V2_TASK_SEED_RESULTS.csv").open()))
    assert len(rows) == 30 * 3 * 3
    table = {}
    for r in rows:
        key = (int(r['task_seed']), int(r['delay']), r['arm'])
        assert key not in table
        assert key[0] in SEEDS and key[1] in DELAYS and key[2] in ARMS
        assert int(r['train_episodes']) == 3000 and int(r['test_episodes']) == 250
        a = float(r['accuracy']); loss = float(r['cross_entropy'])
        assert math.isfinite(a) and 0 <= a <= 1 and math.isfinite(loss)
        table[key] = a
    assert len(table) == 270
    seed_rows = []
    for s in SEEDS:
        means = {a: float(np.mean([table[(s,d,a)] for d in DELAYS])) for a in ARMS}
        seed_rows.append({"task_seed":s,
            "eligibility_minus_no_trace":means["ELIGIBILITY_TRACE"]-means["NO_TRACE"],
            "eligibility_minus_bptt":means["ELIGIBILITY_TRACE"]-means["BPTT"],
            "no_trace_minus_bptt":means["NO_TRACE"]-means["BPTT"]})
    saved_seed_rows = list(csv.DictReader((OUT / "M9V2_PAIRED_SEED_CONTRASTS.csv").open()))
    assert len(saved_seed_rows) == 30
    for a,b in zip(seed_rows,saved_seed_rows):
        for k in a:
            assert abs(float(a[k])-float(b[k])) < 1e-15
    result = json.loads((OUT / "M9V2_PRIMARY_RESULT.json").read_text())
    contrasts = ("eligibility_minus_no_trace","eligibility_minus_bptt","no_trace_minus_bptt")
    for key in contrasts:
        x=np.array([r[key] for r in seed_rows]); saved=result["arm_means_equal_delay"][key]
        lo,hi=ci(x)
        assert abs(float(x.mean())-saved['mean']) < 1e-14
        assert abs(lo-saved['ci95_low']) < 1e-14 and abs(hi-saved['ci95_high']) < 1e-14
    viability={}
    for d in DELAYS:
        x=np.array([table[(s,d,"BPTT")] for s in SEEDS]); lo,hi=ci(x)
        expected=result["bptt_task_viability_by_delay"][str(d)]
        assert abs(x.mean()-expected['bptt_accuracy_mean']) < 1e-14
        assert abs(lo-expected['ci95_low']) < 1e-14 and abs(hi-expected['ci95_high']) < 1e-14
        viability[str(d)]={"mean":float(x.mean()),"ci95_low":lo,"ci95_high":hi,"viable":bool(lo>.25)}
        for s in SEEDS:
            diff=table[(s,d,"ELIGIBILITY_TRACE")]-table[(s,d,"NO_TRACE")]
            assert math.isfinite(diff)
    assert all(v['viable'] for v in viability.values()) == result['all_delays_task_viable']
    runner=ROOT/'model/M9_M5_EPROP_RECURRENT_ASSOCIATION_V2/frozen_runner.py'; contract=ROOT/'summery/M9_M5_EPROP_RECURRENT_ASSOCIATION_V2/M9V2_CONTRACT.md'
    assert sha(runner)==pre['runner_sha256'] and sha(contract)==pre['contract_sha256']
    manifest={"classification":"POST_RESULT_EXPLORATORY_OPTIMIZATION",
      "outcome_data_generated_by":"run_m9_v2.py (pinned preflight hash)",
      "manifest_recovery":"The runner completed all training, test metrics, primary result and report outputs, then failed only while reading a contract path left over from its copied M9-v1 source. Hash and numeric-table verification are recorded in M9V2_POSTRUN_VERIFICATION.json.",
      "contract_sha256":sha(contract),"runner_sha256":sha(runner),
      "result_sha256":sha(OUT/"M9V2_PRIMARY_RESULT.json"),
      "rows_sha256":sha(OUT/"M9V2_TASK_SEED_RESULTS.csv"),
      "task_seed_contrasts_sha256":sha(OUT/"M9V2_PAIRED_SEED_CONTRASTS.csv"),
      "n_metric_rows":len(rows),"n_unique_seed_delay_arm_cells":len(table),"bptt_viability_by_delay":viability}
    (OUT/"M9V2_RUN_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    verification={"verified":True,"checks":{"all_270_cells_present":True,"unique_keys":True,
      "all_metrics_finite":True,"episode_counts_match_contract":True,"per_seed_contrasts_recomputed":True,
      "bootstrap_contrasts_reproduced":True,"bptt_viability_reproduced":True,
      "frozen_runner_and_contract_hashes_match_preflight":True},
      "n_metric_rows":len(rows),"bptt_viability_by_delay":viability,
      "primary_effect":result['primary'],"runner_hash":sha(runner),"contract_hash":sha(contract)}
    (OUT/"M9V2_POSTRUN_VERIFICATION.json").write_text(json.dumps(verification,indent=2)+"\n")
    print(json.dumps(verification,indent=2))

if __name__=='__main__': main()
