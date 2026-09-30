#!/usr/bin/env python3
"""Exploratory synthetic test of motor-state feedback under noisy evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "results" / "M2_PILOT_BAYESIAN_BENCHMARK_V1" / f"rerun_pilot_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
HORIZON = 400
EPISODES = 100
ALPHAS = (0.0, 0.25, 0.5, 0.75, 1.0, -0.5)
HAZARDS = (0.002, 0.01, 0.04)
NOISE_SD = (0.5, 1.0, 1.5)
BURST_PROBABILITY = 0.05
SEED = 20260930


def simulate_episode(
    rng: np.random.Generator, hazard: float, noise_sd: float, alpha: float
) -> tuple[float, float]:
    target = 1.0
    action = 1.0
    artifact = 0.0
    correct = 0
    switches = 0
    for _ in range(HORIZON):
        if rng.random() < hazard:
            target *= -1.0
        if rng.random() < BURST_PROBABILITY:
            artifact = 2.0 * (1.0 if rng.random() < 0.5 else -1.0)
        elif rng.random() >= 0.8:
            artifact = 0.0
        observation = target + rng.normal(0.0, noise_sd) + artifact
        drive = np.tanh(1.5 * (observation + alpha * action))
        next_action = 1.0 if drive >= 0.0 else -1.0
        correct += int(next_action == target)
        switches += int(next_action != action)
        action = next_action
    return correct / HORIZON, switches / HORIZON


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    seed_sequence = np.random.SeedSequence(SEED)
    child_seeds = iter(seed_sequence.spawn(len(HAZARDS) * len(NOISE_SD) * EPISODES))
    rows: list[dict[str, float | int]] = []
    condition_index = 0
    for hazard in HAZARDS:
        for noise_sd in NOISE_SD:
            condition_index += 1
            for episode in range(EPISODES):
                episode_seed = next(child_seeds)
                for alpha in ALPHAS:
                    rng = np.random.default_rng(episode_seed)
                    accuracy, switch_rate = simulate_episode(rng, hazard, noise_sd, alpha)
                    rows.append(
                        {
                            "condition": condition_index,
                            "hazard": hazard,
                            "noise_sd": noise_sd,
                            "episode": episode,
                            "alpha": alpha,
                            "accuracy": accuracy,
                            "switch_rate": switch_rate,
                        }
                    )

    csv_path = OUT / "episode_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary: list[dict[str, float | int]] = []
    for hazard in HAZARDS:
        for noise_sd in NOISE_SD:
            for alpha in ALPHAS:
                subset = [
                    row
                    for row in rows
                    if row["hazard"] == hazard
                    and row["noise_sd"] == noise_sd
                    and row["alpha"] == alpha
                ]
                accuracy = np.asarray([row["accuracy"] for row in subset])
                switching = np.asarray([row["switch_rate"] for row in subset])
                summary.append(
                    {
                        "hazard": hazard,
                        "noise_sd": noise_sd,
                        "alpha": alpha,
                        "accuracy_mean": float(accuracy.mean()),
                        "accuracy_sd_across_episodes": float(accuracy.std(ddof=1)),
                        "switch_rate_mean": float(switching.mean()),
                        "episodes": len(subset),
                    }
                )
    summary_path = OUT / "condition_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "EXPLORATORY_SYNTHETIC_PILOT",
                "seed": SEED,
                "horizon_steps": HORIZON,
                "episodes_per_condition": EPISODES,
                "hazards": HAZARDS,
                "noise_sd": NOISE_SD,
                "burst_probability": BURST_PROBABILITY,
                "burst_persistence": 0.8,
                "alphas": ALPHAS,
                "independent_unit": "episode",
                "row_count": len(rows),
                "python_numpy": np.__version__,
                "outputs": [csv_path.name, summary_path.name],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
