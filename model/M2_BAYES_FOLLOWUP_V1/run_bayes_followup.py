#!/usr/bin/env python3
"""Post-result, exploratory Bayes benchmark for the M2 synthetic task."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "results" / "M2_BAYES_FOLLOWUP_V1" / f"rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
SEED = 20261001
HORIZON = 400
EPISODES = 1000
HAZARDS = (0.002, 0.01, 0.04)
NOISE_SD = (0.5, 1.0, 1.5)
ALPHAS = (0.0, 0.5, 1.0, -0.5)
BURST_PROBABILITY = 0.05
BURST_RESET_PROBABILITY = 0.20

# Hidden state ordering: target in {-1,+1}, artifact in {-2,0,+2}.
TARGETS = (-1.0, 1.0)
ARTIFACTS = (-2.0, 0.0, 2.0)
STATES = tuple((d, b) for d in TARGETS for b in ARTIFACTS)


def transition_matrix(hazard: float) -> np.ndarray:
    matrix = np.zeros((len(STATES), len(STATES)), dtype=float)
    for i, (d, old_b) in enumerate(STATES):
        for j, (next_d, next_b) in enumerate(STATES):
            p_target = 1.0 - hazard if next_d == d else hazard
            # Match run_pilot.py: burst draw first; otherwise reset with prob .2,
            # otherwise retain the prior artifact.
            if next_b in (-2.0, 2.0):
                p_artifact = BURST_PROBABILITY / 2
                if next_b == old_b:
                    p_artifact += (1 - BURST_PROBABILITY) * (1 - BURST_RESET_PROBABILITY)
            else:
                p_artifact = (1 - BURST_PROBABILITY) * BURST_RESET_PROBABILITY
                if old_b == 0:
                    p_artifact += (1 - BURST_PROBABILITY) * (1 - BURST_RESET_PROBABILITY)
            matrix[i, j] = p_target * p_artifact
    assert np.allclose(matrix.sum(axis=1), 1.0)
    return matrix


def bayes_action(prior: np.ndarray, observation: float, noise_sd: float) -> tuple[float, np.ndarray]:
    log_likelihood = np.asarray(
        [-0.5 * ((observation - (d + b)) / noise_sd) ** 2 for d, b in STATES]
    )
    log_likelihood -= log_likelihood.max()
    posterior = prior * np.exp(log_likelihood)
    posterior /= posterior.sum()
    p_positive = sum(p for p, (d, _) in zip(posterior, STATES) if d > 0)
    return (1.0 if p_positive >= 0.5 else -1.0), posterior


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    root_rng = np.random.default_rng(SEED)
    rows: list[dict[str, float | int | str]] = []
    for hazard in HAZARDS:
        transition = transition_matrix(hazard)
        for noise_sd in NOISE_SD:
            for episode in range(EPISODES):
                # One observation/target stream per episode, shared by all controllers.
                rng = np.random.default_rng(root_rng.integers(0, 2**63, dtype=np.int64))
                target, artifact, action = 1.0, 0.0, 1.0
                prior = np.full(len(STATES), 1 / len(STATES), dtype=float)
                prior[STATES.index((1.0, 0.0))] = 1.0
                counts = {f"alpha_{alpha:g}": 0 for alpha in ALPHAS}
                counts["bayes_known_generator"] = 0
                switches = {key: 0 for key in counts}
                previous = {key: 1.0 for key in counts}

                for _ in range(HORIZON):
                    if rng.random() < hazard:
                        target *= -1
                    if rng.random() < BURST_PROBABILITY:
                        artifact = 2.0 * (1.0 if rng.random() < 0.5 else -1.0)
                    elif rng.random() >= (1 - BURST_RESET_PROBABILITY):
                        artifact = 0.0
                    observation = target + rng.normal(0.0, noise_sd) + artifact

                    for alpha in ALPHAS:
                        key = f"alpha_{alpha:g}"
                        drive = np.tanh(1.5 * (observation + alpha * previous[key]))
                        chosen = 1.0 if drive >= 0 else -1.0
                        counts[key] += int(chosen == target)
                        switches[key] += int(chosen != previous[key])
                        previous[key] = chosen

                    prior = prior @ transition
                    chosen, posterior = bayes_action(prior, observation, noise_sd)
                    key = "bayes_known_generator"
                    counts[key] += int(chosen == target)
                    switches[key] += int(chosen != previous[key])
                    previous[key] = chosen
                    prior = posterior

                for controller, correct in counts.items():
                    rows.append(
                        {
                            "hazard": hazard,
                            "noise_sd": noise_sd,
                            "episode": episode,
                            "controller": controller,
                            "accuracy": correct / HORIZON,
                            "switch_rate": switches[controller] / HORIZON,
                        }
                    )

    fields = list(rows[0])
    csv_path = OUT / "episode_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "status": "POST_RESULT_EXPLORATORY_BAYES_FOLLOWUP",
        "seed": SEED,
        "episodes_per_environment": EPISODES,
        "horizon_steps": HORIZON,
        "hazards": HAZARDS,
        "noise_sd": NOISE_SD,
        "burst_probability": BURST_PROBABILITY,
        "burst_reset_probability": BURST_RESET_PROBABILITY,
        "controllers": [*(f"alpha_{a:g}" for a in ALPHAS), "bayes_known_generator"],
        "independent_unit": "episode",
        "row_count": len(rows),
        "numpy_version": np.__version__,
        "model_scope": "known-generator Bayes observer; synthetic task only",
    }
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest["csv_sha256"] = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
