#!/usr/bin/env python3
"""Outcome-informed, recurrence-conditioned topology null for Fish1.5 E1."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/experiment1/postresult_recurrence_null_v1"
ORIGINAL_RUNNER = ROOT / "scripts/run_fish15_experiment1.py"
METRICS_CSV = ROOT / "results/experiment1/FISH15_NEURON_METRICS.csv"
CONTRACT = OUT / "POSTRESULT_NULL_CONTRACT.md"
PREFLIGHT = OUT / "PREFLIGHT.json"
N_NULL = 1000
SEED = 2026093017
MIN_ACCEPTED_BETWEEN = 310
MAX_PROPOSALS = 50_000_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def count_reciprocal_dyads(edge_set: set[tuple[int, int]]) -> int:
    return sum((j, i) in edge_set for i, j in edge_set) // 2


def topology_key(edge_set: set[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(edge_set))


def weighted_matrix(edges: list[tuple[int, int, int]], n: int) -> np.ndarray:
    W = np.zeros((n, n), dtype=np.int64)
    for i, j, weight in edges:
        W[i, j] = weight
    return W


def try_weighted_swap(edges: list[tuple[int, int, int]], edge_set: set[tuple[int, int]],
                      weight_groups: dict[int, list[int]], target_reciprocal_dyads: int,
                      rng: np.random.Generator) -> bool:
    available = [weight for weight, indices in weight_groups.items() if len(indices) >= 2]
    if not available:
        return False
    weight = available[int(rng.integers(len(available)))]
    ix = weight_groups[weight]
    pos = rng.choice(len(ix), size=2, replace=False)
    p, q = int(ix[pos[0]]), int(ix[pos[1]])
    a, b, w1 = edges[p]
    c, d, w2 = edges[q]
    if a == c or b == d:
        return False
    first, second = (a, d), (c, b)
    if first[0] == first[1] or second[0] == second[1] or first == second:
        return False
    if first in edge_set or second in edge_set:
        return False
    edge_set.remove((a, b))
    edge_set.remove((c, d))
    edge_set.add(first)
    edge_set.add(second)
    if count_reciprocal_dyads(edge_set) != target_reciprocal_dyads:
        edge_set.remove(first)
        edge_set.remove(second)
        edge_set.add((a, b))
        edge_set.add((c, d))
        return False
    edges[p] = (first[0], first[1], w1)
    edges[q] = (second[0], second[1], w2)
    return True


def main() -> None:
    if not PREFLIGHT.exists():
        raise RuntimeError("Preflight must be written before execution")
    pre = json.loads(PREFLIGHT.read_text())
    expected = pre["input_sha256"]
    for rel, digest in expected.items():
        if sha256(ROOT / rel) != digest:
            raise RuntimeError(f"input changed since preflight: {rel}")
    if sha256(CONTRACT) != pre["contract_sha256"]:
        raise RuntimeError("contract changed since preflight")
    if sha256(ORIGINAL_RUNNER) != pre["original_runner_sha256"]:
        raise RuntimeError("original graph builder changed since preflight")

    spec = importlib.util.spec_from_file_location("fish15_e1_runner", ORIGINAL_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen graph builder")
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    crosswalk = runner.read_csv(runner.XW)
    crosswalk = [r for r in crosswalk if r.get("type") == "cell" and r.get("functional_id", "").isdigit() and int(r["functional_id"]) > 0]
    cohort_all = runner.read_csv(runner.COV)
    cohort = [r for r in cohort_all if r["structurally_complete"] == "YES"]
    with zipfile.ZipFile(runner.ZIP) as zf:
        W, graph_audit = runner.graph(crosswalk, cohort, zf)
    metric_rows = list(csv.DictReader(METRICS_CSV.open(newline="", encoding="utf-8")))
    primary_rows = [r for r in metric_rows if r["cohort"] == "primary82"]
    ids = [r["functional_id"] for r in cohort]
    if [r["functional_id"] for r in primary_rows] != ids or W.shape != (82, 82):
        raise RuntimeError("frozen 82-node order/shape mismatch")
    y = np.asarray([float(r["dots_persistence"]) for r in primary_rows])
    if not np.isfinite(y).all():
        raise RuntimeError("fixed persistence outcome unexpectedly has missing values")

    B = W > 0
    np.fill_diagonal(B, False)
    observed_edges = [(int(i), int(j), int(W[i, j])) for i, j in zip(*np.where(B))]
    target_recip = count_reciprocal_dyads({(i, j) for i, j, _ in observed_edges})
    degree_in = B.sum(axis=0)
    degree_out = B.sum(axis=1)
    strength_in = W.sum(axis=0)
    strength_out = W.sum(axis=1)
    weight_multiset = np.sort(np.asarray([w for _, _, w in observed_edges], dtype=np.int64))
    observed_lri = runner.metrics(W)["local_recurrence_index"]
    observed_rho = runner.rho(observed_lri, y)
    if target_recip != 2 or len(observed_edges) != 31 or graph_audit["retained_within_cohort_annotations"] != 38:
        raise RuntimeError("observed graph diagnostic disagrees with frozen contract premise")

    rng = np.random.default_rng(SEED)
    edge_set = {(i, j) for i, j, _ in observed_edges}
    edges = observed_edges.copy()
    groups: dict[int, list[int]] = {}
    for ix, (_, _, w) in enumerate(edges):
        groups.setdefault(w, []).append(ix)
    seen = {topology_key(edge_set)}
    rows = []
    accepted_total = 0
    accepted_since_save = 0
    proposals = 0
    while len(rows) < N_NULL and proposals < MAX_PROPOSALS:
        proposals += 1
        if not try_weighted_swap(edges, edge_set, groups, target_recip, rng):
            continue
        accepted_total += 1
        accepted_since_save += 1
        if accepted_since_save < MIN_ACCEPTED_BETWEEN:
            continue
        key = topology_key(edge_set)
        accepted_since_save = 0
        if key in seen:
            continue
        seen.add(key)
        M = weighted_matrix(edges, len(ids))
        mm = runner.metrics(M)
        null_rho = runner.rho(mm["local_recurrence_index"], y)
        if not np.isfinite(null_rho):
            raise RuntimeError("conditioned null yielded an undefined Spearman statistic")
        Mb = M > 0
        null_edges = {(int(i), int(j)) for i, j in zip(*np.where(Mb))}
        rows.append({
            "null_index": len(rows) + 1,
            "topology_sha256": hashlib.sha256(repr(key).encode()).hexdigest(),
            "rho": null_rho,
            "reciprocal_dyad_count": count_reciprocal_dyads(null_edges),
            "unique_nonzero_lri_nodes": int(np.count_nonzero(mm["local_recurrence_index"])),
            "lri_unique_values": int(len(np.unique(mm["local_recurrence_index"]))),
            "accepted_swaps_total": accepted_total,
            "proposals_total": proposals,
            "edge_count_exact": int(len(null_edges) == len(observed_edges)),
            "in_degree_exact": int(np.array_equal(Mb.sum(axis=0), degree_in)),
            "out_degree_exact": int(np.array_equal(Mb.sum(axis=1), degree_out)),
            "in_strength_exact": int(np.array_equal(M.sum(axis=0), strength_in)),
            "out_strength_exact": int(np.array_equal(M.sum(axis=1), strength_out)),
            "global_weight_multiset_exact": int(np.array_equal(np.sort(M[M > 0]), weight_multiset)),
            "reciprocal_dyad_count_exact": int(count_reciprocal_dyads(null_edges) == target_recip),
            "self_loops_absent": int(not np.diag(Mb).any()),
            "binary_topology_unique": 1,
        })
    if len(rows) != N_NULL:
        raise RuntimeError(f"only generated {len(rows)}/{N_NULL} valid unique null states in {proposals} proposals")

    observed_path = OUT / "OBSERVED_GRAPH_DIAGNOSTICS.json"
    observed = {
        "node_count": len(ids), "edge_count": len(observed_edges),
        "retained_synapse_annotation_count": int(W.sum()), "reciprocal_dyad_count": target_recip,
        "nonzero_lri_node_count": int(np.count_nonzero(observed_lri)),
        "unique_lri_value_count": int(len(np.unique(observed_lri))),
        "lri_value_counts": {str(k): int(v) for k, v in Counter(observed_lri.tolist()).items()},
        "observed_primary_rho_recomputed": observed_rho,
        "graph_builder_audit": dict(graph_audit),
    }
    observed_path.write_text(json.dumps(observed, indent=2) + "\n")
    outcsv = OUT / "CONDITIONED_NULL_RESULTS.csv"
    with outcsv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    rhos = np.asarray([r["rho"] for r in rows], dtype=float)
    upper = (1 + int(np.sum(rhos >= observed_rho))) / (N_NULL + 1)
    two_sided = (1 + int(np.sum(np.abs(rhos) >= abs(observed_rho)))) / (N_NULL + 1)
    summary = {
        "status": "POST_RESULT_CONDITIONED_NULL_COMPLETE",
        "interpretation": "Exploratory single-specimen sensitivity only; the original primary result and invalid frozen-null result are unchanged.",
        "n_unique_graphs": len(rows), "proposals": proposals,
        "accepted_swaps_total": accepted_total,
        "minimum_accepted_swaps_between_saved_graphs": MIN_ACCEPTED_BETWEEN,
        "observed_primary_rho": observed_rho,
        "conditioned_null_rho_mean": float(rhos.mean()),
        "conditioned_null_rho_sd": float(rhos.std(ddof=1)),
        "conditioned_null_rho_q025_q975": [float(v) for v in np.quantile(rhos, [0.025, 0.975])],
        "upper_tail_empirical_p": upper,
        "two_sided_absolute_tail_empirical_p_descriptive": two_sided,
        "reciprocal_dyads_conditioned_to": target_recip,
        "all_required_invariants_pass": bool(all(all(int(r[k]) == 1 for k in (
            "edge_count_exact", "in_degree_exact", "out_degree_exact", "in_strength_exact",
            "out_strength_exact", "global_weight_multiset_exact", "reciprocal_dyad_count_exact",
            "self_loops_absent", "binary_topology_unique")) for r in rows)),
    }
    (OUT / "CONDITIONED_NULL_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    manifest = {
        "experiment": "FISH15_E1_POSTRESULT_RECURRENCE_CONDITIONED_NULL_V1",
        "contract": "POSTRESULT_NULL_CONTRACT.md", "preflight": "PREFLIGHT.json",
        "seed": SEED, "n_null": N_NULL, "max_proposals": MAX_PROPOSALS,
        "minimum_accepted_swaps_between_graphs": MIN_ACCEPTED_BETWEEN,
        "conditions": {"node_count": len(ids), "edge_count": len(observed_edges), "reciprocal_dyads": target_recip,
                       "same_weight_only_swaps": True, "preserve_binary_in_out_degree": True,
                       "preserve_per_node_weighted_in_out_strength": True,
                       "preserve_global_weight_multiset": True},
        "input_sha256": expected,
        "outputs": ["OBSERVED_GRAPH_DIAGNOSTICS.json", "CONDITIONED_NULL_RESULTS.csv", "CONDITIONED_NULL_SUMMARY.json"],
    }
    (OUT / "RUN_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
