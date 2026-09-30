#!/usr/bin/env python3
"""Train-on-development, evaluate-on-held-out synthetic state-gating experiment."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "results" / "M2_STATE_GATED_GAIN_V1" / f"rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
MASTER_SEED = 20261001
HORIZON = 400
DEV_EPISODES = 200
TEST_EPISODES = 300
HAZARDS = (0.002, 0.01, 0.04, 0.12)
SIGMA_FORWARD = (0.5, 0.8, 1.2)
SIGMA_VALUES = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
MODE_VALUES = (-1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0, 1.5)
ALPHA_VALUES = SIGMA_VALUES
BOOTSTRAPS = 20_000


def make_episodes(
    rng: np.random.Generator,
    n: int,
    hazard: float,
    sigma_forward: float,
    sigma_reverse: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if sigma_reverse is None:
        sigma_reverse = sigma_forward + 1.6
    target = np.ones(n, dtype=np.int8)
    mode = np.zeros(n, dtype=np.int8)  # 0=forward, 1=reversal
    observations = np.empty((n, HORIZON), dtype=np.float64)
    targets = np.empty((n, HORIZON), dtype=np.int8)
    modes = np.empty((n, HORIZON), dtype=np.int8)
    for t in range(HORIZON):
        target[rng.random(n) < hazard] *= -1
        previous_mode = mode.copy()
        mode[(previous_mode == 0) & (rng.random(n) < 0.03)] = 1
        mode[(previous_mode == 1) & (rng.random(n) < 0.20)] = 0
        sigma = np.where(mode == 0, sigma_forward, sigma_reverse)
        observations[:, t] = target + rng.normal(size=n) * sigma
        targets[:, t] = target
        modes[:, t] = mode
    return observations, targets, modes


def evaluate(
    observations: np.ndarray,
    targets: np.ndarray,
    modes: np.ndarray,
    kind: str,
    params: tuple[float, float, float],
) -> tuple[np.ndarray, np.ndarray]:
    a0, a1, alpha = params
    n, horizon = observations.shape
    action = np.ones(n, dtype=np.int8)
    accuracy = np.zeros(n, dtype=np.float64)
    switches = np.zeros(n, dtype=np.float64)
    for t in range(horizon):
        x = observations[:, t]
        q = modes[:, t]
        if kind == "gated":
            sensory_drive = np.where(q == 0, a0 * x, a1 * x)
        elif kind == "additive":
            mode_code = np.where(q == 0, 1.0, -1.0)
            sensory_drive = a0 * x + a1 * mode_code
        else:
            raise ValueError(f"unknown model kind: {kind}")
        next_action = np.where(sensory_drive + alpha * action >= 0.0, 1, -1)
        accuracy += next_action == targets[:, t]
        switches += next_action != action
        action = next_action.astype(np.int8)
    return accuracy / horizon, switches / horizon


def tune(
    observations: np.ndarray, targets: np.ndarray, modes: np.ndarray, kind: str
) -> tuple[tuple[float, float, float], float]:
    best_params: tuple[float, float, float] | None = None
    best_score = -1.0
    for params in itertools.product(SIGMA_VALUES, MODE_VALUES, ALPHA_VALUES):
        accuracy, _ = evaluate(observations, targets, modes, kind, params)
        score = float(accuracy.mean())
        if score > best_score + 1e-15:
            best_params, best_score = params, score
    assert best_params is not None
    return best_params, best_score


def bayes_filter(
    observations: np.ndarray,
    modes: np.ndarray,
    hazard: float,
    sigma_forward: float,
    sigma_reverse: float | None = None,
) -> np.ndarray:
    if sigma_reverse is None:
        sigma_reverse = sigma_forward + 1.6
    n, horizon = observations.shape
    p_positive = np.ones(n, dtype=np.float64)
    actions = np.ones((n, horizon), dtype=np.int8)
    for t in range(horizon):
        p_positive = p_positive * (1.0 - hazard) + (1.0 - p_positive) * hazard
        sigma = np.where(modes[:, t] == 0, sigma_forward, sigma_reverse)
        log_odds = np.log(p_positive) - np.log1p(-p_positive)
        log_odds += (2.0 * observations[:, t]) / (sigma * sigma)
        # Stable logistic avoids overflow for nearly certain posterior states.
        p_positive = np.where(
            log_odds >= 0.0,
            1.0 / (1.0 + np.exp(-np.minimum(log_odds, 700.0))),
            np.exp(np.maximum(log_odds, -700.0))
            / (1.0 + np.exp(np.maximum(log_odds, -700.0))),
        )
        actions[:, t] = np.where(p_positive >= 0.5, 1, -1)
    return actions


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator) -> list[float]:
    indexes = rng.integers(0, len(values), size=(BOOTSTRAPS, len(values)))
    lo, hi = np.quantile(values[indexes].mean(axis=1), [0.025, 0.975])
    return [float(lo), float(hi)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    seed_iter = iter(np.random.SeedSequence(MASTER_SEED).spawn(1 + len(HAZARDS) * len(SIGMA_FORWARD)))
    dev_obs, dev_target, dev_mode = make_episodes(
        np.random.default_rng(next(seed_iter)), DEV_EPISODES, 0.01, 0.8
    )
    gated_params, gated_dev_score = tune(dev_obs, dev_target, dev_mode, "gated")
    additive_params, additive_dev_score = tune(dev_obs, dev_target, dev_mode, "additive")
    forward_occupancy = 0.20 / (0.03 + 0.20)
    reversal_occupancy = 0.03 / (0.03 + 0.20)
    occupancy_matched_gain = (
        gated_params[0] * forward_occupancy + gated_params[1] * reversal_occupancy
    )

    fitted = {
        "GATED": ("gated", gated_params),
        "ADDITIVE_PARAMETER_MATCHED": ("additive", additive_params),
        "GATED_NO_FEEDBACK": ("gated", (gated_params[0], gated_params[1], 0.0)),
        "GATED_NO_GATE": (
            "gated",
            (occupancy_matched_gain, occupancy_matched_gain, gated_params[2]),
        ),
        "GATED_INVERTED_GATE": ("gated", (gated_params[1], gated_params[0], gated_params[2])),
    }
    rows: list[dict[str, float | int | str]] = []
    summaries = []
    bootstrap_rng = np.random.default_rng(MASTER_SEED + 1)
    for hazard in HAZARDS:
        for sigma_forward in SIGMA_FORWARD:
            obs, target, mode = make_episodes(
                np.random.default_rng(next(seed_iter)), TEST_EPISODES, hazard, sigma_forward
            )
            model_values: dict[str, np.ndarray] = {}
            for name, (kind, params) in fitted.items():
                accuracy, switching = evaluate(obs, target, mode, kind, params)
                model_values[name] = accuracy
                for episode in range(TEST_EPISODES):
                    rows.append(
                        {
                            "hazard": hazard,
                            "sigma_forward": sigma_forward,
                            "sigma_reverse": sigma_forward + 1.6,
                            "episode": episode,
                            "model": name,
                            "accuracy": float(accuracy[episode]),
                            "switch_rate": float(switching[episode]),
                        }
                    )
            bayes_actions = bayes_filter(obs, mode, hazard, sigma_forward)
            bayes_acc = (bayes_actions == target).mean(axis=1)
            model_values["ORACLE_BAYES"] = bayes_acc
            for episode in range(TEST_EPISODES):
                rows.append(
                    {
                        "hazard": hazard,
                        "sigma_forward": sigma_forward,
                        "sigma_reverse": sigma_forward + 1.6,
                        "episode": episode,
                        "model": "ORACLE_BAYES",
                        "accuracy": float(bayes_acc[episode]),
                        "switch_rate": float(np.mean(bayes_actions[episode, 1:] != bayes_actions[episode, :-1])),
                    }
                )
            for model, values in model_values.items():
                summaries.append(
                    {
                        "hazard": hazard,
                        "sigma_forward": sigma_forward,
                        "model": model,
                        "accuracy_mean": float(values.mean()),
                        "accuracy_sd_across_episodes": float(values.std(ddof=1)),
                        "episodes": TEST_EPISODES,
                    }
                )
            for model in ("ADDITIVE_PARAMETER_MATCHED", "GATED_NO_FEEDBACK", "GATED_NO_GATE", "GATED_INVERTED_GATE", "ORACLE_BAYES"):
                diff = model_values["GATED"] - model_values[model]
                summaries.append(
                    {
                        "hazard": hazard,
                        "sigma_forward": sigma_forward,
                        "model": f"PAIRED_GATED_MINUS_{model}",
                        "accuracy_mean": float(diff.mean()),
                        "paired_episode_bootstrap_95ci": bootstrap_ci(diff, bootstrap_rng),
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
                "status": "POST_RESULT_CORRECTED_EXPLORATORY_SYNTHETIC_EXPERIMENT",
                "master_seed": MASTER_SEED,
                "horizon_steps": HORIZON,
                "development_episodes": DEV_EPISODES,
                "test_episodes_per_cell": TEST_EPISODES,
                "development_condition": {"hazard": 0.01, "sigma_forward": 0.8, "sigma_reverse": 2.4},
                "hazards": HAZARDS,
                "sigma_forward_grid": SIGMA_FORWARD,
                "sigma_reverse_rule": "sigma_forward + 1.6",
                "motor_mode_transition": {"forward_to_reversal": 0.03, "reversal_to_forward": 0.20},
                "independent_unit": "episode",
                "parameter_count": {"gated": 3, "additive": 3},
                "grid_combinations_per_architecture": 512,
                "selected_parameters": {"gated": gated_params, "additive": additive_params},
                "no_gate_occupancy_matched_gain": occupancy_matched_gain,
                "control_correction": "occupancy-weighted no-gate replaced the initial arithmetic-mean control after initial outputs; see EXPERIMENT2_CONTROL_CORRECTION.md",
                "stationary_mode_occupancy": {
                    "forward": forward_occupancy,
                    "reversal": reversal_occupancy,
                },
                "development_accuracy": {"gated": gated_dev_score, "additive": additive_dev_score},
                "outputs": ["episode_metrics.csv", "condition_summary.json"],
                "interpretation_limit": "synthetic task only; reversal-state noise contrast is an experimental assumption, not an established biological fact",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
