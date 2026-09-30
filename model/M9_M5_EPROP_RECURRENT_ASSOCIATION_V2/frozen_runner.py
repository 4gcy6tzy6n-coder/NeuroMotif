#!/usr/bin/env python3
"""M9-v1: delayed cue/outcome association with local eligibility, no-trace, and BPTT."""
from __future__ import annotations
import csv, hashlib, json, math, platform, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "results"
CONTRACT = Path(__file__).resolve().parent / "M9_CONTRACT.md"
SEEDS = list(range(200, 230))
DELAYS = (4, 16, 64)
ARMS = ("ELIGIBILITY_TRACE", "NO_TRACE", "BPTT")
N_IN, N_H, N_CLASS = 8, 24, 4
LEAK, TRACE_DECAY, LR, CLIP = 0.1, 0.98, 0.02, 1.0
N_TRAIN, N_TEST, NOISE_SD = 3000, 250, 0.25
N_BOOT, BOOT_SEED = 20_000, 2026093010


def softmax(logits: np.ndarray) -> np.ndarray:
    v = logits - np.max(logits)
    ex = np.exp(v)
    return ex / ex.sum()


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


def episode(rng: np.random.Generator, delay: int, permutation: np.ndarray) -> tuple[np.ndarray, int]:
    cue_class = int(rng.integers(N_CLASS))
    x = rng.normal(0.0, NOISE_SD, (delay + 1, N_IN))
    x[0] = 0.0
    x[0, cue_class] = 1.0
    return x, int(permutation[cue_class])


def forward(x: np.ndarray, w: dict[str, np.ndarray]):
    h = np.zeros(N_H)
    hs, zs, pres = [], [], []
    elig_h = np.zeros((N_H, N_H))
    elig_x = np.zeros((N_H, N_IN))
    elig_b = np.zeros(N_H)
    for xt in x:
        pre = w["Wx"] @ xt + w["Wh"] @ h + w["b"]
        z = np.tanh(pre)
        hnew = (1.0 - LEAK) * h + LEAK * z
        phi = LEAK * (1.0 - z * z)
        elig_h = TRACE_DECAY * elig_h + np.outer(phi, h)
        elig_x = TRACE_DECAY * elig_x + np.outer(phi, xt)
        elig_b = TRACE_DECAY * elig_b + phi
        hs.append(hnew.copy()); zs.append(z.copy()); pres.append(phi.copy())
        h = hnew
    return h, np.asarray(hs), np.asarray(zs), np.asarray(pres), elig_h, elig_x, elig_b


def grads(x, target, w, arm):
    hfinal, hs, zs, phis, e_h, e_x, e_b = forward(x, w)
    logits = w["Wo"] @ hfinal + w["bo"]
    p = softmax(logits)
    delta = p.copy(); delta[target] -= 1.0
    g = {k: np.zeros_like(v) for k, v in w.items()}
    g["Wo"] = np.outer(delta, hfinal)
    g["bo"] = delta
    if arm == "BPTT":
        dh_next = np.zeros(N_H)
        for t in range(len(x) - 1, -1, -1):
            hprev = hs[t - 1] if t else np.zeros(N_H)
            dh_t = (w["Wo"].T @ delta if t == len(x)-1 else np.zeros(N_H)) + dh_next
            du = dh_t * phis[t]
            g["Wx"] += np.outer(du, x[t])
            g["Wh"] += np.outer(du, hprev)
            g["b"] += du
            dh_next = (1.0 - LEAK) * dh_t + w["Wh"].T @ du
    else:
        learning_signal = w["Wo"].T @ delta
        if arm == "NO_TRACE":
            e_h = np.outer(phis[-1], hs[-2] if len(hs) > 1 else np.zeros(N_H))
            e_x = np.outer(phis[-1], x[-1])
            e_b = phis[-1].copy()
        g["Wh"] = learning_signal[:, None] * e_h
        g["Wx"] = learning_signal[:, None] * e_x
        g["b"] = learning_signal * e_b
    return g, int(np.argmax(logits)), float(-math.log(max(float(p[target]), 1e-300)))


def apply_update(w, g):
    norm = math.sqrt(sum(float(np.sum(v*v)) for v in g.values()))
    scale = min(1.0, CLIP / max(norm, 1e-12))
    for k in w:
        w[k] -= LR * scale * g[k]
    if not all(np.isfinite(v).all() for v in w.values()):
        raise FloatingPointError("non-finite model parameters")


def bootstrap_ci(values: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(BOOT_SEED)
    boot = np.empty(N_BOOT)
    for i in range(N_BOOT):
        boot[i] = values[rng.integers(0, len(values), len(values))].mean()
    return float(np.quantile(boot, .025)), float(np.quantile(boot, .975))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in SEEDS:
        task_rng = np.random.default_rng(seed * 100_003 + 17)
        permutation = task_rng.permutation(N_CLASS)
        init = init_weights(seed * 101 + 31)
        for delay in DELAYS:
            train_rng = np.random.default_rng(seed * 1_000_003 + delay * 101 + 1)
            test_rng = np.random.default_rng(seed * 1_000_003 + delay * 101 + 2)
            train = [episode(train_rng, delay, permutation) for _ in range(N_TRAIN)]
            test = [episode(test_rng, delay, permutation) for _ in range(N_TEST)]
            for arm in ARMS:
                w = {k: v.copy() for k, v in init.items()}
                for x, target in train:
                    g, _, _ = grads(x, target, w, arm)
                    apply_update(w, g)
                correct = 0
                losses = []
                for x, target in test:
                    _, pred, loss = grads(x, target, w, "NO_TRACE")
                    correct += int(pred == target); losses.append(loss)
                acc = correct / N_TEST
                rows.append({"task_seed": seed, "delay": delay, "arm": arm,
                             "train_episodes": N_TRAIN, "test_episodes": N_TEST,
                             "accuracy": acc, "cross_entropy": float(np.mean(losses))})
    write_csv(OUT / "M9V2_TASK_SEED_RESULTS.csv", rows)
    per_seed = []
    for seed in SEEDS:
        sub = {(r["delay"], r["arm"]): r["accuracy"] for r in rows if r["task_seed"] == seed}
        row = {"task_seed": seed}
        for arm in ARMS:
            row["mean_accuracy_" + arm.lower()] = float(np.mean([sub[(d, arm)] for d in DELAYS]))
        row["eligibility_minus_no_trace"] = row["mean_accuracy_eligibility_trace"] - row["mean_accuracy_no_trace"]
        row["eligibility_minus_bptt"] = row["mean_accuracy_eligibility_trace"] - row["mean_accuracy_bptt"]
        row["no_trace_minus_bptt"] = row["mean_accuracy_no_trace"] - row["mean_accuracy_bptt"]
        per_seed.append(row)
    write_csv(OUT / "M9V2_PAIRED_SEED_CONTRASTS.csv", per_seed)
    primary = np.array([r["eligibility_minus_no_trace"] for r in per_seed])
    ci = bootstrap_ci(primary)
    stats = {}
    for arm in ARMS:
        stats[arm] = {"mean_accuracy": float(np.mean([r["mean_accuracy_" + arm.lower()] for r in per_seed]))}
    for contrast in ("eligibility_minus_no_trace", "eligibility_minus_bptt", "no_trace_minus_bptt"):
        vals = np.array([r[contrast] for r in per_seed])
        lo, hi = bootstrap_ci(vals)
        stats[contrast] = {"mean": float(vals.mean()), "ci95_low": lo, "ci95_high": hi,
                           "positive_seed_count": int(np.sum(vals > 0)), "n_task_seeds": len(vals)}
    by_delay = {}
    for d in DELAYS:
        vals = []
        for seed in SEEDS:
            sub = {(r["delay"], r["arm"]): r["accuracy"] for r in rows if r["task_seed"] == seed}
            vals.append(sub[(d, "ELIGIBILITY_TRACE")] - sub[(d, "NO_TRACE")])
        arr = np.asarray(vals); lo, hi = bootstrap_ci(arr)
        by_delay[str(d)] = {"eligibility_minus_no_trace_mean": float(arr.mean()), "ci95_low": lo,
                            "ci95_high": hi, "positive_seed_count": int(np.sum(arr > 0))}
    viability = {}
    for d in DELAYS:
        bptt = np.array([next(r["accuracy"] for r in rows if r["task_seed"] == seed and r["delay"] == d and r["arm"] == "BPTT") for seed in SEEDS])
        lo, hi = bootstrap_ci(bptt)
        viability[str(d)] = {"bptt_accuracy_mean": float(bptt.mean()), "ci95_low": lo, "ci95_high": hi,
                             "chance_accuracy": 1.0 / N_CLASS, "task_viable": bool(lo > 1.0 / N_CLASS)}
    result = {"experiment": "M9_M5_EPROP_RECURRENT_ASSOCIATION_V2", "classification": "POST_RESULT_EXPLORATORY_OPTIMIZATION",
              "n_task_seeds": len(SEEDS), "delays": list(DELAYS), "primary_unit": "task_seed",
              "bptt_task_viability_by_delay": viability,
              "all_delays_task_viable": all(v["task_viable"] for v in viability.values()),
              "primary_contrast": "ELIGIBILITY_TRACE - NO_TRACE, equal mean across delays",
              "primary": stats["eligibility_minus_no_trace"], "arm_means_equal_delay": stats,
              "by_delay": by_delay, "parameter_count_per_arm": N_H*N_IN + N_H*N_H + N_H + N_CLASS*N_H + N_CLASS,
              "model": {"input_dim":N_IN,"hidden_units":N_H,"classes":N_CLASS,"leak":LEAK,"trace_decay":TRACE_DECAY,"learning_rate":LR,"clip_norm":CLIP},
              "seed_range": [SEEDS[0], SEEDS[-1]], "bootstrap_resamples": N_BOOT, "bootstrap_seed": BOOT_SEED}
    (OUT / "M9V2_PRIMARY_RESULT.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    write_result_md(result)
    manifest = {"python": platform.python_version(), "numpy": np.__version__,
                "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
                "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "result_sha256": hashlib.sha256((OUT/"M9V2_PRIMARY_RESULT.json").read_bytes()).hexdigest(),
                "rows_sha256": hashlib.sha256((OUT/"M9V2_TASK_SEED_RESULTS.csv").read_bytes()).hexdigest(),
                "task_seed_contrasts_sha256": hashlib.sha256((OUT/"M9V2_PAIRED_SEED_CONTRASTS.csv").read_bytes()).hexdigest()}
    (OUT / "M9V2_RUN_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def write_result_md(r):
    pri = r["primary"]
    lines = ["# M9-v2 — M5 eligibility in a trainable recurrent association task", "",
             "**Classification:** post-result exploratory AI study. This is not biological validation or general transfer.", "",
             f"Primary paired task-seed contrast (`ELIGIBILITY_TRACE − NO_TRACE`, equally averaged over delays 4/16/64): **{pri['mean']:+.4f}** accuracy (95% task-seed bootstrap CI [{pri['ci95_low']:+.4f}, {pri['ci95_high']:+.4f}]); {pri['positive_seed_count']}/{pri['n_task_seeds']} task seeds positive.", "",
             "Equal-delay mean held-out accuracy:"]
    for arm in ARMS:
        lines.append(f"- {arm}: {r['arm_means_equal_delay'][arm]['mean_accuracy']:.4f}")
    for key, label in (("eligibility_minus_bptt", "ELIGIBILITY_TRACE − BPTT"), ("no_trace_minus_bptt", "NO_TRACE − BPTT")):
        s = r["arm_means_equal_delay"][key]
        lines.append(f"- {label}: {s['mean']:+.4f} (95% CI [{s['ci95_low']:+.4f}, {s['ci95_high']:+.4f}])")
    lines += ["", "| Delay | Trace − no-trace | 95% CI | Positive seeds |", "|---:|---:|---:|---:|"]
    for d in DELAYS:
        s = r["by_delay"][str(d)]
        lines.append(f"| {d} | {s['eligibility_minus_no_trace_mean']:+.4f} | [{s['ci95_low']:+.4f}, {s['ci95_high']:+.4f}] | {s['positive_seed_count']}/30 |")
    lines += ["", "Task seeds are the independent units; episodes and delays are paired repeated observations. The model is a fully trainable leaky RNN, not an LTC/LNN implementation. Eligibility is a simplified local learning abstraction inspired by delayed teaching signals. Preserve the BPTT comparison and all negative/uncertain results in interpretation."]
    (OUT / "M9V2_RESULTS.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
