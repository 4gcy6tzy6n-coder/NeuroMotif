#!/usr/bin/env python3
"""Paired episode-level contrasts for the exploratory feedback sweeps."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from datetime import datetime, timezone

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
CONFIGS = (
    (ROOT / "data" / "results" / "M2_ACTION_FEEDBACK_PILOT_V1" / "episode_metrics.csv", 101),
    (ROOT / "data" / "results" / "M2_PILOT_BOUNDARY_EXTENSION_V1" / "episode_metrics.csv", 102),
)
OUT = Path(os.environ.get("M2_OUTPUT_DIR", ROOT / "data" / "results" / "M2_ACTION_FEEDBACK_PILOT_V1" / f"analysis_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"))
BOOTSTRAPS = 20_000


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def paired_bootstrap(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    indices = rng.integers(0, len(values), size=(BOOTSTRAPS, len(values)))
    means = values[indices].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(lo), float(hi)


def main() -> None:
    result = []
    for path, seed in CONFIGS:
        rows = load(path)
        groups: dict[tuple[float, float, float], list[dict[str, str]]] = {}
        for row in rows:
            key = (float(row["hazard"]), float(row["noise_sd"]), float(row["alpha"]))
            groups.setdefault(key, []).append(row)
        conditions = sorted({(key[0], key[1]) for key in groups})
        rng = np.random.default_rng(seed)
        for hazard, noise_sd in conditions:
            by_alpha = {
                alpha: sorted(group, key=lambda row: int(row["episode"]))
                for (h, s, alpha), group in groups.items()
                if h == hazard and s == noise_sd
            }
            base = np.asarray([float(row["accuracy"]) for row in by_alpha[0.0]])
            for comparison in (0.25, 0.5, 0.75, 1.0, -0.5):
                arm = np.asarray(
                    [float(row["accuracy"]) for row in by_alpha[comparison]]
                )
                diff = arm - base
                ci = paired_bootstrap(diff, rng)
                result.append(
                    {
                        "hazard": hazard,
                        "noise_sd": noise_sd,
                        "comparison_alpha_minus_zero": comparison,
                        "mean_paired_accuracy_difference": float(diff.mean()),
                        "paired_episode_bootstrap_95ci": list(ci),
                        "episodes": len(diff),
                        "bootstrap_resamples": BOOTSTRAPS,
                        "independent_unit": "episode",
                    }
                )
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "pilot_paired_contrasts.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
