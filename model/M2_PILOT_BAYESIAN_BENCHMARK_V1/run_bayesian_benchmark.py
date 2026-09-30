#!/usr/bin/env python3
"""Compare pilot controllers with an oracle-parameter exact HMM observer."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

from run_pilot import (
    ALPHAS,
    BURST_PROBABILITY,
    EPISODES,
    HAZARDS,
    HORIZON,
    NOISE_SD,
    SEED,
)


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "results" / "M2_PILOT_BAYESIAN_BENCHMARK_V1" / f"rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"


def sample_episode(
    rng: np.random.Generator, hazard: float, noise_sd: float
) -> tuple[np.ndarray, np.ndarray]:
    target = 1.0
    artifact = 0.0
    observations = np.empty(HORIZON)
    targets = np.empty(HORIZON)
    for t in range(HORIZON):
        if rng.random() < hazard:
            target *= -1.0
        if rng.random() < BURST_PROBABILITY:
            artifact = 2.0 * (1.0 if rng.random() < 0.5 else -1.0)
        elif rng.random() >= 0.8:
            artifact = 0.0
        observations[t] = target + rng.normal(0.0, noise_sd) + artifact
        targets[t] = target
    return observations, targets


def hmm_actions(observations: np.ndarray, hazard: float, noise_sd: float) -> np.ndarray:
    """Filter the joint latent target and persistent burst artifact exactly."""
    targets = np.asarray([-1.0, 1.0])
    artifacts = np.asarray([-2.0, 0.0, 2.0])
    states = [(target, artifact) for target in targets for artifact in artifacts]
    transition = np.zeros((len(states), len(states)))
    for i, (old_target, old_artifact) in enumerate(states):
        for j, (new_target, new_artifact) in enumerate(states):
            p_target = (1.0 - hazard) if new_target == old_target else hazard
            p_new_burst = BURST_PROBABILITY / 2.0
            p_no_burst_clear = (1.0 - BURST_PROBABILITY) * 0.2
            p_no_burst_keep = (1.0 - BURST_PROBABILITY) * 0.8
            if new_artifact != 0.0:
                p_artifact = p_new_burst
                if new_artifact == old_artifact:
                    p_artifact += p_no_burst_keep
            else:
                p_artifact = p_no_burst_clear
                if old_artifact == 0.0:
                    p_artifact += p_no_burst_keep
            transition[i, j] = p_target * p_artifact

    posterior = np.zeros(len(states))
    posterior[states.index((1.0, 0.0))] = 1.0
    actions = np.empty(len(observations))
    means = np.asarray([target + artifact for target, artifact in states])
    target_values = np.asarray([target for target, _ in states])
    for t, observation in enumerate(observations):
        prior = posterior @ transition
        log_likelihood = -0.5 * ((observation - means) / noise_sd) ** 2
        likelihood = np.exp(log_likelihood - log_likelihood.max())
        posterior = prior * likelihood
        posterior /= posterior.sum()
        expected_target = posterior @ target_values
        actions[t] = 1.0 if expected_target >= 0.0 else -1.0
    return actions


def recurrent_actions(observations: np.ndarray, alpha: float) -> np.ndarray:
    action = 1.0
    actions = np.empty(len(observations))
    for t, observation in enumerate(observations):
        drive = np.tanh(1.5 * (observation + alpha * action))
        action = 1.0 if drive >= 0.0 else -1.0
        actions[t] = action
    return actions


def paired_ci(diff: np.ndarray, rng: np.random.Generator) -> list[float]:
    draws = rng.integers(0, len(diff), size=(20_000, len(diff)))
    lo, hi = np.quantile(diff[draws].mean(axis=1), [0.025, 0.975])
    return [float(lo), float(hi)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    child_seeds = iter(
        np.random.SeedSequence(SEED).spawn(len(HAZARDS) * len(NOISE_SD) * EPISODES)
    )
    rows: list[dict[str, float | int | str]] = []
    for hazard in HAZARDS:
        for noise_sd in NOISE_SD:
            for episode in range(EPISODES):
                observations, targets = sample_episode(
                    np.random.default_rng(next(child_seeds)), hazard, noise_sd
                )
                controllers = {
                    "NO_FEEDBACK": recurrent_actions(observations, 0.0),
                    "FEEDBACK_ALPHA_0_75": recurrent_actions(observations, 0.75),
                    "ORACLE_HMM": hmm_actions(observations, hazard, noise_sd),
                }
                for name, actions in controllers.items():
                    rows.append(
                        {
                            "hazard": hazard,
                            "noise_sd": noise_sd,
                            "episode": episode,
                            "controller": name,
                            "accuracy": float(np.mean(actions == targets)),
                        }
                    )
    csv_path = OUT / "episode_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = []
    rng = np.random.default_rng(SEED + 2)
    for hazard in HAZARDS:
        for noise_sd in NOISE_SD:
            arrays = {}
            for controller in ("NO_FEEDBACK", "FEEDBACK_ALPHA_0_75", "ORACLE_HMM"):
                subset = [
                    row for row in rows
                    if row["hazard"] == hazard
                    and row["noise_sd"] == noise_sd
                    and row["controller"] == controller
                ]
                arrays[controller] = np.asarray([row["accuracy"] for row in subset])
            for controller, values in arrays.items():
                summary.append(
                    {
                        "hazard": hazard,
                        "noise_sd": noise_sd,
                        "controller": controller,
                        "accuracy_mean": float(values.mean()),
                        "accuracy_sd_across_episodes": float(values.std(ddof=1)),
                        "episodes": len(values),
                    }
                )
            for controller in ("FEEDBACK_ALPHA_0_75", "ORACLE_HMM"):
                diff = arrays[controller] - arrays["NO_FEEDBACK"]
                summary.append(
                    {
                        "hazard": hazard,
                        "noise_sd": noise_sd,
                        "controller": f"PAIRED_DELTA_{controller}_MINUS_NO_FEEDBACK",
                        "accuracy_mean": float(diff.mean()),
                        "paired_episode_bootstrap_95ci": paired_ci(diff, rng),
                        "episodes": len(diff),
                    }
                )
    summary_path = OUT / "condition_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "EXPLORATORY_ORACLE_BASELINE",
                "seed": SEED,
                "horizon_steps": HORIZON,
                "episodes_per_condition": EPISODES,
                "hazards": HAZARDS,
                "noise_sd": NOISE_SD,
                "controllers": ["NO_FEEDBACK", "FEEDBACK_ALPHA_0_75", "ORACLE_HMM"],
                "independent_unit": "episode",
                "oracle_knows": ["target_switch_hazard", "sensor_noise_sd", "artifact_transition"],
                "warning": "The oracle is a task-specific upper-bound benchmark, not a capacity-matched learned baseline.",
                "outputs": [csv_path.name, summary_path.name],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
