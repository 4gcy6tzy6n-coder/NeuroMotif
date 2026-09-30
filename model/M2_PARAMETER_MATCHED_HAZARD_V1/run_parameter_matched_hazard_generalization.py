#!/usr/bin/env python3
"""Post-result exploratory M2 comparison with two-parameter scalar controllers."""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("M2_OUTPUT_DIR", ROOT / "data" / "results" / "M2_PARAMETER_MATCHED_HAZARD_V1" / f"rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"))
MASTER_SEED = 20260930
TRAIN_SEEDS = tuple(range(10))
TRAIN_EPISODES = 1024
TRAIN_HORIZON = 160
TRAIN_ROUNDS = 4
FIT_EPOCHS_PER_ROUND = 3
BATCH_SIZE = 8192
TEST_EPISODES = 300
HORIZON = 240
BOOTSTRAPS = 20_000
F2R = 0.03
R2F = 0.20
GAIN_F = 1.0
GAIN_R = 0.15
OCC_F = R2F / (F2R + R2F)
OCC_R = F2R / (F2R + R2F)
GAIN_NO_GATE = GAIN_F * OCC_F + GAIN_R * OCC_R
NOISE_PROFILES = {
    "HIGH_REVERSAL_NOISE": (0.2, 1.2),
    "EQUAL_NOISE": (0.7, 0.7),
    "REVERSED_NOISE": (1.2, 0.2),
}
TEST_HAZARDS = (0.005, 0.04)


@dataclass
class Exogenous:
    goals: np.ndarray
    modes: np.ndarray
    measurement_noise: np.ndarray
    process_noise: np.ndarray
    initial_position: np.ndarray
    sigma_forward: np.ndarray
    sigma_reversal: np.ndarray
    hazard: np.ndarray


def sample_exogenous(
    rng: np.random.Generator,
    n: int,
    horizon: int,
    *,
    hazard: float | None = None,
    sigma_forward: float | None = None,
    sigma_reversal: float | None = None,
) -> Exogenous:
    """Draw shared task streams; training randomly samples task parameters by episode."""
    hazards = (
        np.full(n, hazard, dtype=np.float64)
        if hazard is not None
        else np.exp(rng.uniform(np.log(0.002), np.log(0.08), size=n))
    )
    sig_f = (
        np.full(n, sigma_forward, dtype=np.float64)
        if sigma_forward is not None
        else rng.uniform(0.2, 1.2, size=n)
    )
    sig_r = (
        np.full(n, sigma_reversal, dtype=np.float64)
        if sigma_reversal is not None
        else rng.uniform(0.2, 1.2, size=n)
    )
    goals = np.empty((n, horizon), dtype=np.float64)
    modes = np.empty((n, horizon), dtype=np.int8)
    measurement_noise = rng.normal(size=(n, horizon))
    process_noise = rng.normal(0.0, 0.01, size=(n, horizon))
    position = rng.uniform(-4.0, 4.0, size=n)
    goal = rng.choice(np.asarray([-3.0, 3.0]), size=n)
    mode = np.zeros(n, dtype=np.int8)
    for t in range(horizon):
        goal[rng.random(n) < hazards] *= -1.0
        previous_mode = mode.copy()
        to_reversal = (previous_mode == 0) & (rng.random(n) < F2R)
        to_forward = (previous_mode == 1) & (rng.random(n) < R2F)
        mode[to_reversal] = 1
        mode[to_forward] = 0
        goals[:, t] = goal
        modes[:, t] = mode
    return Exogenous(goals, modes, measurement_noise, process_noise, position, sig_f, sig_r, hazards)


def scalar_rollout(
    exogenous: Exogenous,
    weights: tuple[float, float] | None,
    *,
    controller: str,
) -> dict[str, np.ndarray]:
    n, horizon = exogenous.goals.shape
    position = exogenous.initial_position.copy()
    previous_action = np.zeros(n, dtype=np.float64)
    absolute_error = np.empty((n, horizon), dtype=np.float64)
    signed_error = np.empty((n, horizon), dtype=np.float64)
    inside_target = np.empty((n, horizon), dtype=np.float64)
    actions = np.empty((n, horizon), dtype=np.float64)

    for t in range(horizon):
        error = exogenous.goals[:, t] - position
        mode = exogenous.modes[:, t]
        sigma = np.where(mode == 0, exogenous.sigma_forward, exogenous.sigma_reversal)
        observation = error + sigma * exogenous.measurement_noise[:, t]
        if controller in {"FIXED_GATED", "LEARNED_GATED"}:
            gain = np.where(mode == 0, GAIN_F, GAIN_R)
        else:
            gain = GAIN_NO_GATE

        if controller == "PRIVILEGED_TEACHER":
            action = np.tanh(0.7 * error)
        else:
            assert weights is not None
            w_sensory, w_action = weights
            action = np.tanh(w_sensory * gain * (observation / 5.0) + w_action * previous_action)

        absolute_error[:, t] = np.abs(error)
        signed_error[:, t] = error
        inside_target[:, t] = (np.abs(error) < 0.5).astype(np.float64)
        actions[:, t] = action
        position = np.clip(position + 0.15 * action + exogenous.process_noise[:, t], -5.0, 5.0)
        previous_action = action

    switch_delays: list[list[float]] = [[] for _ in range(n)]
    for t in range(1, horizon):
        switched = exogenous.goals[:, t] != exogenous.goals[:, t - 1]
        for episode in np.flatnonzero(switched):
            end = min(horizon - 3, t + 39)
            delay = 40.0
            for candidate in range(t, end + 1):
                aligned = (
                    actions[episode, candidate : candidate + 3]
                    * signed_error[episode, candidate : candidate + 3]
                    > 0.0
                )
                if np.all(aligned):
                    delay = float(candidate - t)
                    break
            switch_delays[episode].append(delay)
    return {
        "mean_absolute_error": absolute_error.mean(axis=1),
        "target_zone_fraction": inside_target.mean(axis=1),
        "direction_switch_delay": np.asarray(
            [np.mean(values) if values else np.nan for values in switch_delays], dtype=np.float64
        ),
    }


def collect_dagger_data(
    exogenous: Exogenous,
    weights: tuple[float, float],
    *,
    gated: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n, horizon = exogenous.goals.shape
    position = exogenous.initial_position.copy()
    previous_action = np.zeros(n, dtype=np.float64)
    features = np.empty((n, horizon, 2), dtype=np.float32)
    labels = np.empty((n, horizon), dtype=np.float32)
    w_sensory, w_action = weights
    for t in range(horizon):
        error = exogenous.goals[:, t] - position
        mode = exogenous.modes[:, t]
        sigma = np.where(mode == 0, exogenous.sigma_forward, exogenous.sigma_reversal)
        observation = error + sigma * exogenous.measurement_noise[:, t]
        gain = np.where(mode == 0, GAIN_F, GAIN_R) if gated else GAIN_NO_GATE
        effective_observation = gain * observation / 5.0
        features[:, t, 0] = effective_observation
        features[:, t, 1] = previous_action
        labels[:, t] = np.tanh(0.7 * error)
        action = np.tanh(w_sensory * effective_observation + w_action * previous_action)
        position = np.clip(position + 0.15 * action + exogenous.process_noise[:, t], -5.0, 5.0)
        previous_action = action
    return features.reshape(-1, 2), labels.reshape(-1), exogenous.hazard


def fit_two_weights(
    features: np.ndarray,
    labels: np.ndarray,
    start_weights: tuple[float, float],
    seed: int,
) -> tuple[tuple[float, float], float]:
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    x = torch.from_numpy(features)
    y = torch.from_numpy(labels[:, None])
    weights = torch.nn.Parameter(torch.tensor(start_weights, dtype=torch.float32))
    optimizer = torch.optim.Adam([weights], lr=0.01)
    rng = torch.Generator().manual_seed(seed + 1)
    last_loss = float("nan")
    batch_size = min(BATCH_SIZE, x.shape[0])
    for _ in range(FIT_EPOCHS_PER_ROUND):
        order = torch.randperm(x.shape[0], generator=rng)
        losses = []
        for start in range(0, x.shape[0], batch_size):
            idx = order[start : start + batch_size]
            prediction = torch.tanh(x[idx] @ weights)
            loss = torch.mean((prediction[:, None] - y[idx]) ** 2)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach()))
        last_loss = float(np.mean(losses))
    return (float(weights.detach()[0]), float(weights.detach()[1])), last_loss


def train_controller(seed: int, *, gated: bool) -> dict[str, object]:
    weights = (3.0, 0.12)
    feature_parts: list[np.ndarray] = []
    label_parts: list[np.ndarray] = []
    losses: list[float] = []
    data_seed = np.random.SeedSequence([MASTER_SEED, seed, 7701])
    round_seeds = data_seed.spawn(TRAIN_ROUNDS)
    for round_index, child in enumerate(round_seeds):
        exogenous = sample_exogenous(
            np.random.default_rng(child), TRAIN_EPISODES, TRAIN_HORIZON
        )
        features, labels, _ = collect_dagger_data(exogenous, weights, gated=gated)
        feature_parts.append(features)
        label_parts.append(labels)
        weights, loss = fit_two_weights(
            np.concatenate(feature_parts),
            np.concatenate(label_parts),
            weights,
            seed=MASTER_SEED + seed * 100 + round_index,
        )
        losses.append(loss)
    return {"weights": weights, "round_training_mse": losses, "trainable_parameters": 2}


def hierarchical_bootstrap(differences: np.ndarray, seed: int) -> tuple[float, float]:
    """Bootstrap seeds, then paired episode rows within each hazard×noise cell."""
    # shape: training seed × six environment cells × episodes
    rng = np.random.default_rng(seed)
    n_seeds, n_cells, n_episodes = differences.shape
    draws = np.empty(BOOTSTRAPS, dtype=np.float64)
    batch = 100
    for start in range(0, BOOTSTRAPS, batch):
        size = min(batch, BOOTSTRAPS - start)
        chosen_seeds = rng.integers(0, n_seeds, size=(size, n_seeds))
        selected = differences[chosen_seeds]
        episode_idx = rng.integers(0, n_episodes, size=(size, n_seeds, n_cells, n_episodes))
        resampled = np.take_along_axis(selected, episode_idx, axis=3).mean(axis=3)
        draws[start : start + size] = resampled.mean(axis=(1, 2))
    return tuple(float(x) for x in np.quantile(draws, [0.025, 0.975]))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(1)
    rows: list[dict[str, object]] = []
    train_records: list[dict[str, object]] = []
    learned_differences = np.empty((len(TRAIN_SEEDS), len(TEST_HAZARDS) * len(NOISE_PROFILES), TEST_EPISODES))
    primary_cell_summaries: list[dict[str, object]] = []
    teacher_records: list[dict[str, object]] = []

    for train_index, train_seed in enumerate(TRAIN_SEEDS):
        learned_gate = train_controller(train_seed, gated=True)
        learned_no_gate = train_controller(train_seed, gated=False)
        train_records.append({"train_seed": train_seed, "learned_gated": learned_gate, "learned_no_gate": learned_no_gate})

        cell_index = 0
        for hazard_index, hazard in enumerate(TEST_HAZARDS):
            for profile_index, (profile, (sigma_f, sigma_r)) in enumerate(NOISE_PROFILES.items()):
                cell_rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, 8800, hazard_index, profile_index]))
                exogenous = sample_exogenous(
                    cell_rng,
                    TEST_EPISODES,
                    HORIZON,
                    hazard=hazard,
                    sigma_forward=sigma_f,
                    sigma_reversal=sigma_r,
                )
                outputs: dict[str, dict[str, np.ndarray]] = {
                    "FIXED_GATED": scalar_rollout(exogenous, (3.0, 0.12), controller="FIXED_GATED"),
                    "FIXED_NO_GATE": scalar_rollout(exogenous, (3.0, 0.12), controller="FIXED_NO_GATE"),
                    "LEARNED_GATED": scalar_rollout(exogenous, learned_gate["weights"], controller="LEARNED_GATED"),
                    "LEARNED_NO_GATE": scalar_rollout(exogenous, learned_no_gate["weights"], controller="LEARNED_NO_GATE"),
                    "PRIVILEGED_TEACHER": scalar_rollout(exogenous, None, controller="PRIVILEGED_TEACHER"),
                }
                cell_diff = outputs["LEARNED_GATED"]["mean_absolute_error"] - outputs["LEARNED_NO_GATE"]["mean_absolute_error"]
                learned_differences[train_index, cell_index] = cell_diff
                primary_cell_summaries.append(
                    {
                        "train_seed": train_seed,
                        "hazard": hazard,
                        "noise_profile": profile,
                        "mean_paired_mae_difference_gated_minus_no_gate": float(cell_diff.mean()),
                        "episodes": TEST_EPISODES,
                    }
                )
                for policy, metrics in outputs.items():
                    for episode in range(TEST_EPISODES):
                        rows.append(
                            {
                                "train_seed": train_seed,
                                "hazard": hazard,
                                "noise_profile": profile,
                                "sigma_forward": sigma_f,
                                "sigma_reversal": sigma_r,
                                "episode": episode,
                                "policy": policy,
                                "mean_absolute_error": float(metrics["mean_absolute_error"][episode]),
                                "target_zone_fraction": float(metrics["target_zone_fraction"][episode]),
                                "direction_switch_delay": float(metrics["direction_switch_delay"][episode]),
                            }
                        )
                cell_index += 1

    primary_mean = float(learned_differences.mean())
    primary_ci = hierarchical_bootstrap(learned_differences, MASTER_SEED + 991)
    for row in rows:
        if row["policy"] == "PRIVILEGED_TEACHER":
            teacher_records.append(row)

    csv_path = OUT / "episode_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "status": "POST_RESULT_EXPLORATORY_PARAMETER_MATCHED_GENERALIZATION_COMPLETE",
        "primary_estimand": "equal-cell and equal-training-seed average paired episode MAE difference (LEARNED_GATED - LEARNED_NO_GATE)",
        "primary_mean_difference": primary_mean,
        "primary_hierarchical_bootstrap_95ci": list(primary_ci),
        "primary_interpretation": (
            "GATED_LOWER_ERROR" if primary_ci[1] < 0 else
            "GATED_HIGHER_ERROR" if primary_ci[0] > 0 else
            "INCONCLUSIVE_INTERVAL_INCLUDES_ZERO"
        ),
        "episodes_per_seed_per_cell": TEST_EPISODES,
        "training_seeds": len(TRAIN_SEEDS),
        "cell_summaries": primary_cell_summaries,
        "notes": [
            "All experiments are synthetic and outcome-informed by prior M2 results.",
            "Both learned controllers have exactly two trainable scalar parameters and use matched DAgger training streams, episode counts, and optimizer settings.",
            "Test hazards were not used as fixed training conditions; noise profile values were previously seen in earlier M2 experiments.",
            "The privileged teacher is not a fair deployable baseline.",
            "No biological measurements or outcomes were used.",
        ],
        "files": [csv_path.name, "run_manifest.json"],
    }
    (OUT / "primary_result.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "experiment": "M2_PARAMETER_MATCHED_HAZARD_GENERALIZATION",
        "status": summary["status"],
        "seed": MASTER_SEED,
        "training": {
            "independent_training_seeds": list(TRAIN_SEEDS),
            "episodes_per_round": TRAIN_EPISODES,
            "horizon": TRAIN_HORIZON,
            "dagger_rounds": TRAIN_ROUNDS,
            "fit_epochs_per_round": FIT_EPOCHS_PER_ROUND,
            "batch_size": BATCH_SIZE,
            "task_distribution": "hazard log-uniform [0.002,0.08], sigma_F and sigma_R independently uniform [0.2,1.2] per episode",
            "controllers": train_records,
        },
        "test": {
            "episodes_per_cell": TEST_EPISODES,
            "horizon": HORIZON,
            "hazards": TEST_HAZARDS,
            "noise_profiles": NOISE_PROFILES,
            "mode_transitions": {"forward_to_reversal": F2R, "reversal_to_forward": R2F},
            "paired_exogenous_streams": True,
        },
        "independent_unit": "training seed for model-fit variability; episode nested within environment cell for rollout variability",
        "primary_result_file": "primary_result.json",
        "episode_metrics_file": csv_path.name,
        "warnings": [
            "post-result exploratory study; no confirmatory interpretation",
            "synthetic state/noise design is not a verified biological implementation",
            "does not compare against generic GRU/RNN families or establish broad task-generator generalization",
        ],
    }
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"primary_mean_difference": primary_mean, "ci95": primary_ci, "interpretation": summary["primary_interpretation"], "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
