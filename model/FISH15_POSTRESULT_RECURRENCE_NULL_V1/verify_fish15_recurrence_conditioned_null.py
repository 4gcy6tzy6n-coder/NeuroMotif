#!/usr/bin/env python3
"""Independently recompute summaries from the saved Fish1.5 conditional-null table."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/experiment1/postresult_recurrence_null_v1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    summary = json.loads((OUT / "CONDITIONED_NULL_SUMMARY.json").read_text())
    observed = json.loads((OUT / "OBSERVED_GRAPH_DIAGNOSTICS.json").read_text())
    manifest = json.loads((OUT / "RUN_MANIFEST.json").read_text())
    preflight = json.loads((OUT / "PREFLIGHT.json").read_text())
    rows = list(csv.DictReader((OUT / "CONDITIONED_NULL_RESULTS.csv").open(newline="", encoding="utf-8")))
    assert len(rows) == 1000 == int(summary["n_unique_graphs"])
    hashes = [r["topology_sha256"] for r in rows]
    assert len(set(hashes)) == 1000
    rhos = np.asarray([float(r["rho"]) for r in rows])
    assert np.isfinite(rhos).all()
    invariant_fields = ("edge_count_exact", "in_degree_exact", "out_degree_exact", "in_strength_exact",
                        "out_strength_exact", "global_weight_multiset_exact", "reciprocal_dyad_count_exact",
                        "self_loops_absent", "binary_topology_unique")
    assert all(int(r[k]) == 1 for r in rows for k in invariant_fields)
    assert all(int(r["reciprocal_dyad_count"]) == 2 for r in rows)
    assert all(int(r["lri_unique_values"]) >= 2 for r in rows)
    observed_rows = list(csv.DictReader((ROOT / "results/experiment1/FISH15_NEURON_METRICS.csv").open(newline="", encoding="utf-8")))
    primary = [r for r in observed_rows if r["cohort"] == "primary82"]
    x = np.asarray([float(r["local_recurrence_index"]) for r in primary])
    y = np.asarray([float(r["dots_persistence"]) for r in primary])
    observed_rho = float(spearmanr(x, y).statistic)
    assert np.isclose(observed_rho, float(observed["observed_primary_rho_recomputed"]), rtol=0, atol=1e-14)
    upper = (1 + int(np.sum(rhos >= observed_rho))) / 1001
    two_sided = (1 + int(np.sum(np.abs(rhos) >= abs(observed_rho)))) / 1001
    q = np.quantile(rhos, [0.025, 0.975]).tolist()
    mean = float(rhos.mean())
    sd = float(rhos.std(ddof=1))
    centered = rhos - mean
    denom = float(np.dot(centered, centered))
    acf = [1.0]
    for lag in range(1, 51):
        acf.append(float(np.dot(centered[:-lag], centered[lag:]) / denom))
    pair_sum = 0.0
    for k in range(1, len(acf) - 1, 2):
        pair = acf[k] + acf[k + 1]
        if pair <= 0:
            break
        pair_sum += pair
    ess_ips = float(len(rhos) / (1 + 2 * pair_sum))
    assert np.isclose(upper, summary["upper_tail_empirical_p"], rtol=0, atol=1e-15)
    assert np.isclose(two_sided, summary["two_sided_absolute_tail_empirical_p_descriptive"], rtol=0, atol=1e-15)
    assert np.allclose(q, summary["conditioned_null_rho_q025_q975"], rtol=0, atol=1e-14)
    assert np.isclose(mean, summary["conditioned_null_rho_mean"], rtol=0, atol=1e-14)
    assert np.isclose(sd, summary["conditioned_null_rho_sd"], rtol=0, atol=1e-14)
    for rel, expected in preflight["input_sha256"].items():
        assert sha256(ROOT / rel) == expected, f"changed input: {rel}"
    assert sha256(ROOT / "scripts/run_fish15_recurrence_conditioned_null.py") == preflight["runner_sha256"]
    result = {
        "status": "SUMMARY_AND_REPORTED_INVARIANT_AUDIT_PASSED",
        "checks": {
            "unique_null_rows": len(rows), "all_rhos_finite": True, "unique_topology_hashes": len(set(hashes)),
            "all_saved_invariant_flags_equal_one": True, "all_graphs_condition_on_two_reciprocal_dyads": True,
            "all_graphs_have_nonconstant_lri": True, "observed_rho_independently_recomputed": observed_rho,
            "upper_tail_empirical_p_recomputed": upper, "two_sided_absolute_tail_empirical_p_recomputed": two_sided,
            "null_quantiles_mean_sd_recomputed": {"q025_q975": q, "mean": mean, "sd": sd},
            "rho_chain_autocorrelation_lag1": acf[1], "rho_chain_autocorrelation_lags1to20": acf[1:21],
            "approx_initial_positive_sequence_ess": ess_ips,
            "approx_mc_standard_error_for_null_mean": float(sd / np.sqrt(ess_ips)),
            "mixing_status": "UNRESOLVED_HIGH_SERIAL_AUTOCORRELATION",
            "preflight_input_hashes_unchanged": True, "simulation_runner_hash_matches_preflight": True,
        },
        "verification_boundary": "Per-graph edge lists were not saved; graph invariants are checked from the runner's per-graph invariant flags and audited against the frozen same-weight swap implementation, not independently reconstructed from edge states. Chain autocorrelation is high; ESS is an approximate diagnostic, and the empirical null tail is not treated as well-mixed confirmatory inference.",
        "verification_script_sha256": sha256(Path(__file__)),
    }
    (OUT / "POSTRUN_VERIFICATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
