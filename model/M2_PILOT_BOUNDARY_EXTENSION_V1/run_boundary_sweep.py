#!/usr/bin/env python3
"""Predeclared exploratory extension to locate the feedback failure boundary."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

from run_pilot import ALPHAS, BURST_PROBABILITY, EPISODES, HORIZON, NOISE_SD, SEED, simulate_episode


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "results" / "M2_PILOT_BOUNDARY_EXTENSION_V1" / f"rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
HAZARDS = (0.08, 0.16, 0.32)
EXTENSION_SEED = SEED + 1


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    combinations = len(HAZARDS) * len(NOISE_SD) * EPISODES
    seeds = iter(np.random.SeedSequence(EXTENSION_SEED).spawn(combinations))
    rows: list[dict[str, float | int]] = []
    condition = 0
    for hazard in HAZARDS:
        for noise_sd in NOISE_SD:
            condition += 1
            for episode in range(EPISODES):
                episode_seed = next(seeds)
                for alpha in ALPHAS:
                    accuracy, switch_rate = simulate_episode(
                        np.random.default_rng(episode_seed), hazard, noise_sd, alpha
                    )
                    rows.append(
                        {
                            "condition": condition,
                            "hazard": hazard,
                            "noise_sd": noise_sd,
                            "episode": episode,
                            "alpha": alpha,
                            "accuracy": accuracy,
                            "switch_rate": switch_rate,
                        }
                    )

    with (OUT / "episode_metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = []
    for hazard in HAZARDS:
        for noise_sd in NOISE_SD:
            for alpha in ALPHAS:
                subset = [
                    row for row in rows
                    if row["hazard"] == hazard
                    and row["noise_sd"] == noise_sd
                    and row["alpha"] == alpha
                ]
                values = np.asarray([row["accuracy"] for row in subset])
                summary.append(
                    {
                        "hazard": hazard,
                        "noise_sd": noise_sd,
                        "alpha": alpha,
                        "accuracy_mean": float(values.mean()),
                        "accuracy_sd_across_episodes": float(values.std(ddof=1)),
                        "episodes": len(values),
                    }
                )
    (OUT / "condition_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "POST_PILOT_EXPLORATORY_BOUNDARY_EXTENSION",
                "seed": EXTENSION_SEED,
                "horizon_steps": HORIZON,
                "episodes_per_condition": EPISODES,
                "hazards": HAZARDS,
                "noise_sd": NOISE_SD,
                "burst_probability": BURST_PROBABILITY,
                "alphas": ALPHAS,
                "independent_unit": "episode",
                "row_count": len(rows),
                "purpose": "map where action-state feedback ceases to help; not confirmatory",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
