#!/usr/bin/env python3
"""Retrain the generic GRU with on-policy imitation to reduce teacher-forcing shift."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import torch

from run_closed_loop_experiment import (
    ACTION_FEEDBACK,
    FORWARD_OCCUPANCY,
    FORWARD_TO_REVERSAL,
    HAZARDS,
    HORIZON,
    MASTER_SEED,
    NO_GATE_GAIN,
    NOISE_PROFILES,
    REVERSAL_OCCUPANCY,
    REVERSAL_TO_FORWARD,
    SENSORY_GAIN_FORWARD,
    SENSORY_GAIN_REVERSAL,
    TEST_EPISODES,
    TRAIN_EPISODES,
    TRAIN_HORIZON,
    ActionGRU,
    make_training_data,
    rollout,
    sample_exogenous,
    train_gru,
)


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "results" / "M2_DAGGER_GRU_FOLLOWUP_V1" / f"rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
DAgger_ROUNDS = 3
FINE_TUNE_EPOCHS_PER_ROUND = 4


def collect_on_policy_data(
    model: ActionGRU,
    exogenous,
    sigma_f: float,
    sigma_r: float,
) -> tuple[np.ndarray, np.ndarray]:
    n, horizon = exogenous.goals.shape
    position = exogenous.initial_position.copy()
    previous_action = np.zeros(n, dtype=np.float64)
    inputs = np.empty((n, horizon, 3), dtype=np.float32)
    labels = np.empty((n, horizon, 1), dtype=np.float32)
    hidden = None
    model.eval()
    for t in range(horizon):
        error = exogenous.goals[:, t] - position
        sigma = np.where(exogenous.modes[:, t] == 0, sigma_f, sigma_r)
        observation = error + sigma * exogenous.measurement_noise[:, t]
        mode_code = np.where(exogenous.modes[:, t] == 0, 1.0, -1.0)
        inputs[:, t, 0] = observation / 5.0
        inputs[:, t, 1] = mode_code
        inputs[:, t, 2] = previous_action
        labels[:, t, 0] = np.tanh(0.7 * error)
        model_input = torch.from_numpy(inputs[:, t, :].copy()[:, None, :])
        with torch.no_grad():
            state, hidden = model.gru(model_input, hidden)
            action = torch.tanh(model.readout(state[:, 0, :])).squeeze(1).numpy()
        position = np.clip(position + 0.15 * action + exogenous.process_noise[:, t], -5.0, 5.0)
        previous_action = action
    return inputs, labels


def fit_epochs(model: ActionGRU, x: np.ndarray, y: np.ndarray, seed: int, epochs: int, lr: float) -> list[float]:
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    inputs = torch.from_numpy(x)
    labels = torch.from_numpy(y)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    losses = []
    for _ in range(epochs):
        order = torch.randperm(inputs.shape[0])
        epoch_loss = 0.0
        batches = 0
        for start in range(0, inputs.shape[0], 32):
            indexes = order[start : start + 32]
            prediction = model(inputs[indexes])
            loss = torch.mean((prediction - labels[indexes]) ** 2)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.detach())
            batches += 1
        losses.append(epoch_loss / batches)
    return losses


def train_dagger(seed: int) -> tuple[ActionGRU, dict[str, object]]:
    model, pretrain_info = train_gru(seed)
    pretrain_exogenous = sample_exogenous(
        np.random.default_rng(seed), TRAIN_EPISODES, TRAIN_HORIZON, hazard=0.01
    )
    teacher_x, teacher_y = make_training_data(pretrain_exogenous, sigma_f=0.2, sigma_r=1.2)
    x_parts = [teacher_x]
    y_parts = [teacher_y]
    round_losses = []
    rng = np.random.default_rng(seed + 10)
    for round_index in range(DAgger_ROUNDS):
        exogenous = sample_exogenous(
            rng, TRAIN_EPISODES, TRAIN_HORIZON, hazard=0.01
        )
        on_x, on_y = collect_on_policy_data(model, exogenous, sigma_f=0.2, sigma_r=1.2)
        x_parts.append(on_x)
        y_parts.append(on_y)
        losses = fit_epochs(
            model,
            np.concatenate(x_parts, axis=0),
            np.concatenate(y_parts, axis=0),
            seed=seed + 20 + round_index,
            epochs=FINE_TUNE_EPOCHS_PER_ROUND,
            lr=0.001,
        )
        round_losses.append(losses)
    return model.eval(), {
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "pretraining": pretrain_info,
        "dagger_rounds": DAgger_ROUNDS,
        "fine_tune_epochs_per_round": FINE_TUNE_EPOCHS_PER_ROUND,
        "dagger_loss_by_round": round_losses,
        "aggregated_training_episodes": TRAIN_EPISODES * (DAgger_ROUNDS + 1),
        "training_horizon": TRAIN_HORIZON,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    model, train_info = train_dagger(MASTER_SEED + 1)
    cells = len(HAZARDS) * len(NOISE_PROFILES)
    child_seeds = iter(np.random.SeedSequence(MASTER_SEED).spawn(cells))
    rows = []
    summaries = []
    rng_boot = np.random.default_rng(MASTER_SEED + 3)
    policies = (
        "GATED_FEEDBACK",
        "NO_GATE_FEEDBACK",
        "GATED_NO_FEEDBACK",
        "UNGATED_MEMORYLESS",
        "TRAINED_GRU",
        "PRIVILEGED_TEACHER",
    )
    for hazard in HAZARDS:
        for profile, (sigma_f, sigma_r) in NOISE_PROFILES.items():
            exogenous = sample_exogenous(
                np.random.default_rng(next(child_seeds)), TEST_EPISODES, HORIZON, hazard
            )
            outputs = {}
            for policy in policies:
                outputs[policy] = rollout(
                    exogenous,
                    sigma_f,
                    sigma_r,
                    policy,
                    model=model if policy == "TRAINED_GRU" else None,
                )
                for episode in range(TEST_EPISODES):
                    rows.append(
                        {
                            "hazard": hazard,
                            "noise_profile": profile,
                            "sigma_forward": sigma_f,
                            "sigma_reversal": sigma_r,
                            "episode": episode,
                            "policy": policy,
                            "mean_absolute_error": float(outputs[policy]["mean_absolute_error"][episode]),
                            "target_zone_fraction": float(outputs[policy]["target_zone_fraction"][episode]),
                            "direction_switch_delay": float(outputs[policy]["direction_switch_delay"][episode]),
                        }
                    )
            for policy, output in outputs.items():
                summaries.append(
                    {
                        "hazard": hazard,
                        "noise_profile": profile,
                        "policy": policy,
                        "mean_absolute_error": float(output["mean_absolute_error"].mean()),
                        "mean_target_zone_fraction": float(output["target_zone_fraction"].mean()),
                        "mean_direction_switch_delay": float(np.nanmean(output["direction_switch_delay"])),
                        "episodes": TEST_EPISODES,
                    }
                )
            for baseline in ("NO_GATE_FEEDBACK", "UNGATED_MEMORYLESS", "TRAINED_GRU", "PRIVILEGED_TEACHER"):
                for metric in ("mean_absolute_error", "target_zone_fraction"):
                    delta = outputs["GATED_FEEDBACK"][metric] - outputs[baseline][metric]
                    indexes = rng_boot.integers(0, len(delta), size=(20_000, len(delta)))
                    ci = np.quantile(delta[indexes].mean(axis=1), [0.025, 0.975])
                    summaries.append(
                        {
                            "hazard": hazard,
                            "noise_profile": profile,
                            "policy": f"PAIRED_GATED_MINUS_{baseline}",
                            "metric": metric,
                            "mean_difference": float(delta.mean()),
                            "paired_episode_bootstrap_95ci": [float(ci[0]), float(ci[1])],
                            "episodes": TEST_EPISODES,
                        }
                    )

    csv_path = OUT / "episode_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "condition_summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    (OUT / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "POST_RESULT_DAGGER_BASELINE_REPAIR",
                "seed": MASTER_SEED + 1,
                "training": train_info,
                "test_grid": {"hazards": HAZARDS, "noise_profiles": NOISE_PROFILES, "episodes_per_cell": TEST_EPISODES},
                "independent_unit": "episode",
                "outputs": [csv_path.name, "condition_summary.json"],
                "warning": "post-result baseline repair; no confirmatory interpretation",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
