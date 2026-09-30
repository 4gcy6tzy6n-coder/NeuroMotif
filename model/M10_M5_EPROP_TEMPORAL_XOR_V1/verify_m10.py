#!/usr/bin/env python3
"""Independent schema, checksum, and seed-level statistic audit for M10 outputs."""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
CONTRACT = HERE / "M10_CONTRACT.md"
RUNNER = HERE / "run_m10.py"
SEEDS = list(range(300, 330))
DELAYS = (4, 16, 64)
ARMS = ("ELIGIBILITY_TRACE", "NO_TRACE", "BPTT")
N_BOOT = 20_000
BOOT_SEED = 2026093010


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ci(values: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, len(values), size=(N_BOOT, len(values)))
    boot = values[idx].mean(axis=1)
    return float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tol


def main() -> None:
    metrics_path = OUT / "M10_TASK_SEED_RESULTS.csv"
    contrasts_path = OUT / "M10_PAIRED_SEED_CONTRASTS.csv"
    result_path = OUT / "M10_PRIMARY_RESULT.json"
    manifest_path = OUT / "M10_RUN_MANIFEST.json"
    preflight_path = OUT / "M10_PREFLIGHT.json"
    with metrics_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(SEEDS) * len(DELAYS) * len(ARMS), f"unexpected row count: {len(rows)}"
    table = {}
    for r in rows:
        key = (int(r["task_seed"]), int(r["delay"]), r["arm"])
        assert key not in table, f"duplicate key: {key}"
        assert key[0] in SEEDS and key[1] in DELAYS and key[2] in ARMS, f"out-of-contract key: {key}"
        acc, loss = float(r["accuracy"]), float(r["cross_entropy"])
        assert math.isfinite(acc) and 0 <= acc <= 1, f"invalid accuracy at {key}"
        assert math.isfinite(loss) and loss >= 0, f"invalid loss at {key}"
        assert int(r["train_episodes"]) == 6000 and int(r["test_episodes"]) == 500
        table[key] = acc
    assert len(table) == len(rows)
    per_seed = []
    for seed in SEEDS:
        m = {arm: np.mean([table[(seed, d, arm)] for d in DELAYS]) for arm in ARMS}
        per_seed.append({"task_seed": seed, "ELIGIBILITY_TRACE": m["ELIGIBILITY_TRACE"],
                         "NO_TRACE": m["NO_TRACE"], "BPTT": m["BPTT"],
                         "eligibility_minus_no_trace": m["ELIGIBILITY_TRACE"] - m["NO_TRACE"],
                         "eligibility_minus_bptt": m["ELIGIBILITY_TRACE"] - m["BPTT"],
                         "no_trace_minus_bptt": m["NO_TRACE"] - m["BPTT"]})
    with contrasts_path.open(newline="", encoding="utf-8") as f:
        saved = list(csv.DictReader(f))
    assert len(saved) == len(SEEDS)
    for got, want in zip(saved, per_seed):
        assert int(got["task_seed"]) == want["task_seed"]
        for k in ("eligibility_minus_no_trace", "eligibility_minus_bptt", "no_trace_minus_bptt"):
            assert close(float(got[k]), want[k]), f"contrast mismatch {k}, seed {want['task_seed']}"
    result = json.loads(result_path.read_text())
    for arm in ARMS:
        mean = float(np.mean([r[arm] for r in per_seed]))
        assert close(mean, result["arm_means_equal_delay"][arm]["mean_accuracy"]), f"arm mean mismatch: {arm}"
    for contrast in ("eligibility_minus_no_trace", "eligibility_minus_bptt", "no_trace_minus_bptt"):
        vals = np.array([r[contrast] for r in per_seed])
        lo, hi = ci(vals)
        saved_stat = result["arm_means_equal_delay"][contrast]
        assert close(float(vals.mean()), saved_stat["mean"]), f"contrast mean mismatch: {contrast}"
        assert close(lo, saved_stat["ci95_low"]), f"CI lower mismatch: {contrast}"
        assert close(hi, saved_stat["ci95_high"]), f"CI upper mismatch: {contrast}"
        assert int(np.sum(vals > 0)) == saved_stat["positive_seed_count"]
    for d in DELAYS:
        vals_trace = np.array([table[(s, d, "ELIGIBILITY_TRACE")] for s in SEEDS])
        vals_no = np.array([table[(s, d, "NO_TRACE")] for s in SEEDS])
        vals_bptt = np.array([table[(s, d, "BPTT")] for s in SEEDS])
        lo, hi = ci(vals_trace - vals_no)
        got = result["by_delay"][str(d)]
        assert close(float(vals_trace.mean()), got["trace_mean_accuracy"])
        assert close(float(vals_no.mean()), got["no_trace_mean_accuracy"])
        assert close(float(vals_bptt.mean()), got["bptt_mean_accuracy"])
        assert close(float((vals_trace-vals_no).mean()), got["trace_minus_no_trace"])
        assert close(lo, got["trace_minus_no_trace_ci95"][0]) and close(hi, got["trace_minus_no_trace_ci95"][1])
        blo, bhi = ci(vals_bptt)
        v = result["bptt_viability_by_delay"][str(d)]
        assert close(blo, v["ci95_low"]) and close(bhi, v["ci95_high"])
        assert bool(blo > 0.5) == bool(v["task_viable"])
    preflight = json.loads(preflight_path.read_text())
    assert preflight["contract_sha256"] == sha(CONTRACT)
    assert preflight["runner_sha256"] == sha(RUNNER)
    assert preflight["outcome_metrics_computed"] is False
    manifest = json.loads(manifest_path.read_text())
    checks = {"contract_sha256": sha(CONTRACT), "runner_sha256": sha(RUNNER),
              "preflight_sha256": sha(preflight_path), "metrics_sha256": sha(metrics_path),
              "contrasts_sha256": sha(contrasts_path), "primary_result_sha256": sha(result_path)}
    for key, value in checks.items():
        assert manifest[key] == value, f"manifest hash mismatch: {key}"
    report = {"experiment": "M10_M5_EPROP_TEMPORAL_XOR_V1", "status": "PASS",
              "checks": {"metric_rows": len(rows), "unique_task_seed_delay_arm_keys": len(table),
                         "paired_seed_rows": len(saved), "all_metric_values_finite": True,
                         "all_metrics_within_contract_bounds": True, "seed_contrasts_recomputed": True,
                         "primary_and_delay_statistics_recomputed": True, "bptt_viability_recomputed": True,
                         "source_and_result_hashes_match": True},
              "max_bptt_gradient_preflight_error": preflight["bptt_gradient_check"]["max_absolute_error"],
              "primary": result["primary"], "bptt_viability_by_delay": result["bptt_viability_by_delay"]}
    verify_path = OUT / "M10_POSTRUN_VERIFICATION.json"
    verify_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    manifest["postrun_verification"] = "PASS"
    manifest["verifier_sha256"] = sha(Path(__file__))
    manifest["verification_sha256"] = sha(verify_path)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
