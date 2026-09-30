#!/usr/bin/env python3
"""M10: local eligibility versus no-trace and BPTT on delayed two-cue XOR."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
CONTRACT = HERE / "M10_CONTRACT.md"
SEEDS = tuple(range(300, 330))
DELAYS = (4, 16, 64)
ARMS = ("ELIGIBILITY_TRACE", "NO_TRACE", "BPTT")
N_IN, N_H, N_CLASS = 4, 24, 2
LEAK, TRACE_DECAY, LR, CLIP = 0.1, 0.98, 0.02, 1.0
N_TRAIN, N_TEST, NOISE_SD = 6000, 500, 0.25
N_BOOT, BOOT_SEED = 20_000, 2026093010


def softmax(logits: np.ndarray) -> np.ndarray:
    e = np.exp(logits - np.max(logits))
    return e / np.sum(e)


def init_weights(seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.normal(size=(N_H, N_H)))
    return {
        "Wx": rng.normal(0.0, 0.5, (N_H, N_IN)),
        "Wh": 0.9 * q,
        "b": np.zeros(N_H),
        "Wo": rng.normal(0.0, 0.01, (N_CLASS, N_H)),
        "bo": np.zeros(N_CLASS),
    }


def make_episode(rng: np.random.Generator, delay: int) -> tuple[np.ndarray, int, tuple[int, int]]:
    a, b = (int(v) for v in rng.integers(0, 2, size=2))
    # First cue, D irrelevant distractor steps, second cue, terminal blank/readout.
    x = np.zeros((delay + 3, N_IN), dtype=np.float64)
    x[0, a] = 1.0
    x[1 : delay + 1] = rng.normal(0.0, NOISE_SD, (delay, N_IN))
    x[delay + 1, 2 + b] = 1.0
    return x, a ^ b, (a, b)


def forward(x: np.ndarray, w: dict[str, np.ndarray]):
    h = np.zeros(N_H)
    hs, phis = [], []
    e_h = np.zeros((N_H, N_H))
    e_x = np.zeros((N_H, N_IN))
    e_b = np.zeros(N_H)
    for xt in x:
        hprev = h
        z = np.tanh(w["Wx"] @ xt + w["Wh"] @ hprev + w["b"])
        phi = LEAK * (1.0 - z * z)
        h = (1.0 - LEAK) * hprev + LEAK * z
        e_h = TRACE_DECAY * e_h + np.outer(phi, hprev)
        e_x = TRACE_DECAY * e_x + np.outer(phi, xt)
        e_b = TRACE_DECAY * e_b + phi
        hs.append(h.copy())
        phis.append(phi.copy())
    return h, np.asarray(hs), np.asarray(phis), e_h, e_x, e_b


def gradients(x: np.ndarray, target: int, w: dict[str, np.ndarray], arm: str):
    h_final, hs, phis, e_h, e_x, e_b = forward(x, w)
    logits = w["Wo"] @ h_final + w["bo"]
    p = softmax(logits)
    delta = p.copy()
    delta[target] -= 1.0
    g = {k: np.zeros_like(v) for k, v in w.items()}
    g["Wo"] = np.outer(delta, h_final)
    g["bo"] = delta
    if arm == "BPTT":
        dh_next = np.zeros(N_H)
        for t in range(len(x) - 1, -1, -1):
            hprev = hs[t - 1] if t else np.zeros(N_H)
            dh = (w["Wo"].T @ delta if t == len(x) - 1 else np.zeros(N_H)) + dh_next
            du = dh * phis[t]
            g["Wx"] += np.outer(du, x[t])
            g["Wh"] += np.outer(du, hprev)
            g["b"] += du
            dh_next = (1.0 - LEAK) * dh + w["Wh"].T @ du
    else:
        signal = w["Wo"].T @ delta
        if arm == "NO_TRACE":
            hprev = hs[-2] if len(hs) > 1 else np.zeros(N_H)
            e_h = np.outer(phis[-1], hprev)
            e_x = np.outer(phis[-1], x[-1])
            e_b = phis[-1].copy()
        g["Wh"] = signal[:, None] * e_h
        g["Wx"] = signal[:, None] * e_x
        g["b"] = signal * e_b
    loss = -math.log(max(float(p[target]), 1e-300))
    return g, int(np.argmax(logits)), loss


def apply_update(w: dict[str, np.ndarray], g: dict[str, np.ndarray]) -> None:
    norm = math.sqrt(sum(float(np.sum(v * v)) for v in g.values()))
    scale = min(1.0, CLIP / max(norm, 1e-12))
    for k in w:
        w[k] -= LR * scale * g[k]
    if not all(np.isfinite(v).all() for v in w.values()):
        raise FloatingPointError("non-finite model parameters")


def bootstrap_ci(values: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, len(values), size=(N_BOOT, len(values)))
    boot = values[idx].mean(axis=1)
    return float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def preflight() -> dict:
    w = init_weights(78123)
    rng = np.random.default_rng(9917)
    x, target, _ = make_episode(rng, 4)
    g, _, _ = gradients(x, target, w, "BPTT")
    eps = 1e-6
    checks = [("Wx", 0, 0), ("Wx", 3, 2), ("Wh", 0, 1), ("Wh", 7, 9), ("b", 4), ("Wo", 1, 5), ("bo", 0)]
    errors = []
    for item in checks:
        key, *ij = item
        index = tuple(ij)
        original = float(w[key][index])
        w[key][index] = original + eps
        loss_plus = gradients(x, target, w, "BPTT")[2]
        w[key][index] = original - eps
        loss_minus = gradients(x, target, w, "BPTT")[2]
        w[key][index] = original
        numeric = (loss_plus - loss_minus) / (2.0 * eps)
        analytic = float(g[key][index])
        errors.append({"parameter": f"{key}{index}", "absolute_error": abs(numeric - analytic),
                       "numeric": numeric, "analytic": analytic})
    max_error = max(x["absolute_error"] for x in errors)
    label_table = {f"{a}{b}": a ^ b for a in (0, 1) for b in (0, 1)}
    timing = {"first_cue_t": 0, "distractor_steps": 4, "second_cue_t": 5, "readout_t": 6,
              "sequence_length": len(x)}
    if label_table != {"00": 0, "01": 1, "10": 1, "11": 0}:
        raise AssertionError("XOR truth-table check failed")
    if timing != {"first_cue_t": 0, "distractor_steps": 4, "second_cue_t": 5, "readout_t": 6,
                  "sequence_length": 7}:
        raise AssertionError("input timing check failed")
    if max_error > 2e-6 or not all(np.isfinite(v).all() for v in w.values()):
        raise AssertionError(f"BPTT gradient preflight failed (max_abs_error={max_error})")
    payload = {
        "experiment": "M10_M5_EPROP_TEMPORAL_XOR_V1", "status": "PREFLIGHT_PASSED_BEFORE_OUTCOME_RUN",
        "classification": "POST_RESULT_EXPLORATORY_ARTIFICIAL_BENCHMARK",
        "python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform(),
        "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "config": {"seeds": [SEEDS[0], SEEDS[-1]], "delays": list(DELAYS), "arms": list(ARMS),
                   "train_episodes": N_TRAIN, "test_episodes": N_TEST, "hidden_units": N_H,
                   "learning_rate": LR, "trace_decay": TRACE_DECAY, "clip_norm": CLIP,
                   "bootstrap_resamples": N_BOOT, "bootstrap_seed": BOOT_SEED},
        "xor_truth_table": label_table, "timing_check": timing,
        "bptt_gradient_check": {"method": "central_finite_difference", "epsilon": eps,
                                "max_absolute_error": max_error, "checks": errors},
        "outcome_metrics_computed": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "M10_PREFLIGHT.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    return payload


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for seed in SEEDS:
        init = init_weights(seed * 101 + 31)
        for delay in DELAYS:
            train_rng = np.random.default_rng(seed * 1_000_003 + delay * 101 + 1)
            test_rng = np.random.default_rng(seed * 1_000_003 + delay * 101 + 2)
            train = [make_episode(train_rng, delay) for _ in range(N_TRAIN)]
            test = [make_episode(test_rng, delay) for _ in range(N_TEST)]
            for arm in ARMS:
                w = {k: v.copy() for k, v in init.items()}
                for x, target, _ in train:
                    g, _, _ = gradients(x, target, w, arm)
                    apply_update(w, g)
                correct = 0
                loss_total = 0.0
                for x, target, _ in test:
                    _, pred, loss = gradients(x, target, w, "NO_TRACE")
                    correct += int(pred == target)
                    loss_total += loss
                rows.append({"task_seed": seed, "delay": delay, "arm": arm,
                             "train_episodes": N_TRAIN, "test_episodes": N_TEST,
                             "accuracy": correct / N_TEST, "cross_entropy": loss_total / N_TEST})
    write_csv(OUT / "M10_TASK_SEED_RESULTS.csv", rows)
    per_seed = []
    for seed in SEEDS:
        sub = {(r["delay"], r["arm"]): r["accuracy"] for r in rows if r["task_seed"] == seed}
        drow = {"task_seed": seed}
        for arm in ARMS:
            drow["mean_accuracy_" + arm.lower()] = float(np.mean([sub[(d, arm)] for d in DELAYS]))
        for contrast, a, b in (("eligibility_minus_no_trace", "ELIGIBILITY_TRACE", "NO_TRACE"),
                               ("eligibility_minus_bptt", "ELIGIBILITY_TRACE", "BPTT"),
                               ("no_trace_minus_bptt", "NO_TRACE", "BPTT")):
            drow[contrast] = drow["mean_accuracy_" + a.lower()] - drow["mean_accuracy_" + b.lower()]
        per_seed.append(drow)
    write_csv(OUT / "M10_PAIRED_SEED_CONTRASTS.csv", per_seed)
    stats = {}
    for arm in ARMS:
        stats[arm] = {"mean_accuracy": float(np.mean([r["mean_accuracy_" + arm.lower()] for r in per_seed]))}
    for contrast in ("eligibility_minus_no_trace", "eligibility_minus_bptt", "no_trace_minus_bptt"):
        vals = np.array([r[contrast] for r in per_seed])
        lo, hi = bootstrap_ci(vals)
        stats[contrast] = {"mean": float(vals.mean()), "ci95_low": lo, "ci95_high": hi,
                           "positive_seed_count": int(np.sum(vals > 0)), "n_task_seeds": len(vals)}
    by_delay, viability = {}, {}
    for delay in DELAYS:
        sub = {(r["task_seed"], r["arm"]): r["accuracy"] for r in rows if r["delay"] == delay}
        trace = np.array([sub[(s, "ELIGIBILITY_TRACE")] for s in SEEDS])
        no_trace = np.array([sub[(s, "NO_TRACE")] for s in SEEDS])
        bptt = np.array([sub[(s, "BPTT")] for s in SEEDS])
        lo, hi = bootstrap_ci(trace - no_trace)
        by_delay[str(delay)] = {"trace_mean_accuracy": float(trace.mean()), "no_trace_mean_accuracy": float(no_trace.mean()),
                                "bptt_mean_accuracy": float(bptt.mean()), "trace_minus_no_trace": float((trace-no_trace).mean()),
                                "trace_minus_no_trace_ci95": [lo, hi], "positive_seed_count": int(np.sum(trace > no_trace))}
        blo, bhi = bootstrap_ci(bptt)
        viability[str(delay)] = {"bptt_mean_accuracy": float(bptt.mean()), "ci95_low": blo, "ci95_high": bhi,
                                 "chance_accuracy": 0.5, "task_viable": bool(blo > 0.5)}
    result = {"experiment": "M10_M5_EPROP_TEMPORAL_XOR_V1", "classification": "POST_RESULT_EXPLORATORY_ARTIFICIAL_BENCHMARK",
              "primary_unit": "task_seed", "n_task_seeds": len(SEEDS), "seed_range": [SEEDS[0], SEEDS[-1]],
              "task": "two-cue temporal XOR with uninformative Gaussian distractors",
              "delays": list(DELAYS), "primary_contrast": "ELIGIBILITY_TRACE - NO_TRACE, equally averaged over delays",
              "primary": stats["eligibility_minus_no_trace"], "arm_means_equal_delay": stats,
              "by_delay": by_delay, "bptt_viability_by_delay": viability,
              "all_delays_viable": all(v["task_viable"] for v in viability.values()),
              "chance_accuracy": 0.5, "parameter_count": sum(v.size for v in init_weights(SEEDS[0]*101+31).values()),
              "model": {"input_dim": N_IN, "hidden_units": N_H, "outputs": N_CLASS, "leak": LEAK,
                        "trace_decay": TRACE_DECAY, "learning_rate": LR, "clip_norm": CLIP},
              "train_episodes_per_seed_delay_arm": N_TRAIN, "test_episodes_per_seed_delay_arm": N_TEST,
              "bootstrap_resamples": N_BOOT, "bootstrap_seed": BOOT_SEED}
    (OUT / "M10_PRIMARY_RESULT.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    write_result_md(result)
    manifest = {"experiment": result["experiment"], "python": platform.python_version(), "numpy": np.__version__,
                "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
                "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "preflight_sha256": hashlib.sha256((OUT / "M10_PREFLIGHT.json").read_bytes()).hexdigest(),
                "metrics_sha256": hashlib.sha256((OUT / "M10_TASK_SEED_RESULTS.csv").read_bytes()).hexdigest(),
                "contrasts_sha256": hashlib.sha256((OUT / "M10_PAIRED_SEED_CONTRASTS.csv").read_bytes()).hexdigest(),
                "primary_result_sha256": hashlib.sha256((OUT / "M10_PRIMARY_RESULT.json").read_bytes()).hexdigest(),
                "postrun_verification": "PENDING"}
    (OUT / "M10_RUN_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return result


def write_result_md(result: dict) -> None:
    p = result["primary"]
    lines = ["# M10 — Delayed two-cue XOR integration", "",
             "**Classification:** post-result exploratory synthetic recurrent-network benchmark; not biological validation or general AI transfer.", "",
             f"Primary task-seed contrast (`ELIGIBILITY_TRACE − NO_TRACE`, equal mean over delays): **{p['mean']:+.4f}** accuracy (95% bootstrap CI [{p['ci95_low']:+.4f}, {p['ci95_high']:+.4f}]); {p['positive_seed_count']}/{p['n_task_seeds']} task seeds positive.", "",
             "Equal-delay mean held-out accuracy:"]
    for arm in ARMS:
        lines.append(f"- {arm}: {result['arm_means_equal_delay'][arm]['mean_accuracy']:.4f}")
    for c, label in (("eligibility_minus_bptt", "ELIGIBILITY_TRACE − BPTT"), ("no_trace_minus_bptt", "NO_TRACE − BPTT")):
        s = result["arm_means_equal_delay"][c]
        lines.append(f"- {label}: {s['mean']:+.4f} (95% CI [{s['ci95_low']:+.4f}, {s['ci95_high']:+.4f}])")
    lines += ["", "| Delay | Trace accuracy | No-trace accuracy | BPTT accuracy | Trace − no-trace (95% CI) |", "|---:|---:|---:|---:|---:|"]
    for d in DELAYS:
        s = result["by_delay"][str(d)]
        lines.append(f"| {d} | {s['trace_mean_accuracy']:.4f} | {s['no_trace_mean_accuracy']:.4f} | {s['bptt_mean_accuracy']:.4f} | {s['trace_minus_no_trace']:+.4f} [{s['trace_minus_no_trace_ci95'][0]:+.4f}, {s['trace_minus_no_trace_ci95'][1]:+.4f}] |")
    lines += ["", f"BPTT task viability across the delay grid: **{'PASS' if result['all_delays_viable'] else 'FAIL'}** (lower 95% seed-bootstrap bound must exceed 0.50 at every delay).", "",
              "Task seeds are the independent units; examples and delays are repeated/paired. This experiment tests an artificial two-cue XOR sequence in one leaky tanh RNN. Eligibility is a simplified local teaching-signal abstraction; this is not a liquid neural network, biological validation, or connectome transfer."]
    (OUT / "M10_RESULTS.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(), indent=2))
    else:
        result = run()
        print(json.dumps({"experiment": result["experiment"], "primary": result["primary"],
                          "all_delays_viable": result["all_delays_viable"], "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
