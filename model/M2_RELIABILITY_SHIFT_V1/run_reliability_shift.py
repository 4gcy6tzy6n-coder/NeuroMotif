#!/usr/bin/env python3
"""Post-result sensitivity test: freeze parameters, shift state/reliability mapping."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

from run_state_gated_experiment import (
    HAZARDS,
    HORIZON,
    SIGMA_FORWARD,
    TEST_EPISODES,
    bayes_filter,
    evaluate,
    make_episodes,
)


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "results" / "M2_RELIABILITY_SHIFT_V1" / f"rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
MASTER_SEED = 20261002
BOOTSTRAPS = 20_000


def paired_ci(values: np.ndarray, rng: np.random.Generator) -> list[float]:
    indexes = rng.integers(0, len(values), size=(BOOTSTRAPS, len(values)))
    low, high = np.quantile(values[indexes].mean(axis=1), [0.025, 0.975])
    return [float(low), float(high)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    primary_path = ROOT / "data" / "results" / "M2_STATE_GATED_GAIN_V1" / "run_manifest.json"
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    gated = tuple(primary["selected_parameters"]["gated"])
    additive = tuple(primary["selected_parameters"]["additive"])
    forward_occupancy = 0.20 / (0.03 + 0.20)
    reversal_occupancy = 0.03 / (0.03 + 0.20)
    mean_gain = gated[0] * forward_occupancy + gated[1] * reversal_occupancy
    models = {
        "GATED_FIXED": ("gated", gated),
        "ADDITIVE_FIXED": ("additive", additive),
        "NO_GATE_FIXED": ("gated", (mean_gain, mean_gain, gated[2])),
        "NO_FEEDBACK_FIXED": ("gated", (gated[0], gated[1], 0.0)),
    }
    conditions = []
    for relation in ("EQUAL", "REVERSED"):
        for sigma_forward in SIGMA_FORWARD:
            sigma_reverse = sigma_forward if relation == "EQUAL" else max(0.2, sigma_forward - 0.4)
            for hazard in HAZARDS:
                conditions.append((relation, sigma_forward, sigma_reverse, hazard))

    children = iter(np.random.SeedSequence(MASTER_SEED).spawn(len(conditions)))
    rng_ci = np.random.default_rng(MASTER_SEED + 1)
    rows: list[dict[str, float | int | str]] = []
    summaries = []
    for relation, sigma_forward, sigma_reverse, hazard in conditions:
        observations, targets, modes = make_episodes(
            np.random.default_rng(next(children)),
            TEST_EPISODES,
            hazard,
            sigma_forward,
            sigma_reverse=sigma_reverse,
        )
        scores = {}
        for name, (kind, params) in models.items():
            accuracy, switch_rate = evaluate(observations, targets, modes, kind, params)
            scores[name] = accuracy
            for episode in range(TEST_EPISODES):
                rows.append(
                    {
                        "reliability_relation": relation,
                        "hazard": hazard,
                        "sigma_forward": sigma_forward,
                        "sigma_reverse": sigma_reverse,
                        "episode": episode,
                        "model": name,
                        "accuracy": float(accuracy[episode]),
                        "switch_rate": float(switch_rate[episode]),
                    }
                )
        oracle_actions = bayes_filter(
            observations,
            modes,
            hazard,
            sigma_forward,
            sigma_reverse=sigma_reverse,
        )
        scores["ORACLE_BAYES"] = (oracle_actions == targets).mean(axis=1)
        for episode, score in enumerate(scores["ORACLE_BAYES"]):
            rows.append(
                {
                    "reliability_relation": relation,
                    "hazard": hazard,
                    "sigma_forward": sigma_forward,
                    "sigma_reverse": sigma_reverse,
                    "episode": episode,
                    "model": "ORACLE_BAYES",
                    "accuracy": float(score),
                    "switch_rate": float(np.mean(oracle_actions[episode, 1:] != oracle_actions[episode, :-1])),
                }
            )
        for name, values in scores.items():
            summaries.append(
                {
                    "reliability_relation": relation,
                    "hazard": hazard,
                    "sigma_forward": sigma_forward,
                    "sigma_reverse": sigma_reverse,
                    "model": name,
                    "accuracy_mean": float(values.mean()),
                    "accuracy_sd_across_episodes": float(values.std(ddof=1)),
                    "episodes": TEST_EPISODES,
                }
            )
        for baseline in ("ADDITIVE_FIXED", "NO_GATE_FIXED", "NO_FEEDBACK_FIXED", "ORACLE_BAYES"):
            delta = scores["GATED_FIXED"] - scores[baseline]
            summaries.append(
                {
                    "reliability_relation": relation,
                    "hazard": hazard,
                    "sigma_forward": sigma_forward,
                    "sigma_reverse": sigma_reverse,
                    "model": f"PAIRED_GATED_MINUS_{baseline}",
                    "accuracy_mean": float(delta.mean()),
                    "paired_episode_bootstrap_95ci": paired_ci(delta, rng_ci),
                    "episodes": TEST_EPISODES,
                }
            )

    with (OUT / "episode_metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "condition_summary.json").write_text(
        json.dumps(summaries, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "POST_RESULT_FIXED_PARAMETER_SENSITIVITY",
                "master_seed": MASTER_SEED,
                "parameter_source": str(primary_path),
                "selected_parameters_reused_without_retuning": {
                    "gated": gated,
                    "additive": additive,
                    "occupancy_matched_no_gate_gain": mean_gain,
                },
                "episode_count_per_cell": TEST_EPISODES,
                "horizons": HORIZON,
                "reliability_relations": {
                    "EQUAL": "sigma_reverse = sigma_forward",
                    "REVERSED": "sigma_reverse = max(0.2, sigma_forward - 0.4)",
                },
                "hazards": HAZARDS,
                "sigma_forward_grid": SIGMA_FORWARD,
                "independent_unit": "episode",
                "warning": "post-result sensitivity analysis; do not describe as a preregistered confirmatory test",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
