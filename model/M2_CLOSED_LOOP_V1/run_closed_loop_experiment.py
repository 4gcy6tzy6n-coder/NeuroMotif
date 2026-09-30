#!/usr/bin/env python3
"""Closed-loop 1-D target tracking with state-gated and trainable recurrent policies."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import torch
from torch import nn


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "results" / "M2_CLOSED_LOOP_V1" / f"rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
MASTER_SEED = 20261003
HORIZON = 240
TRAIN_HORIZON = 160
TRAIN_EPISODES = 512
TEST_EPISODES = 300
HAZARDS = (0.002, 0.02, 0.08)
NOISE_PROFILES = {
    "HIGH_REVERSAL_NOISE": (0.2, 1.2),
    "EQUAL_NOISE": (0.7, 0.7),
    "REVERSED_NOISE": (1.2, 0.2),
}
BOOTSTRAPS = 20_000
FORWARD_TO_REVERSAL = 0.03
REVERSAL_TO_FORWARD = 0.20
SENSORY_GAIN_FORWARD = 1.0
SENSORY_GAIN_REVERSAL = 0.15
ACTION_FEEDBACK = 0.20
FORWARD_OCCUPANCY = REVERSAL_TO_FORWARD / (FORWARD_TO_REVERSAL + REVERSAL_TO_FORWARD)
REVERSAL_OCCUPANCY = FORWARD_TO_REVERSAL / (FORWARD_TO_REVERSAL + REVERSAL_TO_FORWARD)
NO_GATE_GAIN = (
    SENSORY_GAIN_FORWARD * FORWARD_OCCUPANCY
    + SENSORY_GAIN_REVERSAL * REVERSAL_OCCUPANCY
)


@dataclass
class Exogenous:
    goals: np.ndarray
    modes: np.ndarray  # 0=F, 1=R
    measurement_noise: np.ndarray
    process_noise: np.ndarray
    initial_position: np.ndarray


class ActionGRU(nn.Module):
    def __init__(self, hidden: int = 16) -> None:
        super().__init__()
        self.gru = nn.GRU(input_size=3, hidden_size=hidden, batch_first=True)
        self.readout = nn.Linear(hidden, 1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        states, _ = self.gru(inputs)
        return torch.tanh(self.readout(states))


def sample_exogenous(
    rng: np.random.Generator,
    n: int,
    horizon: int,
    hazard: float,
) -> Exogenous:
    goals = np.empty((n, horizon), dtype=np.float64)
    modes = np.empty((n, horizon), dtype=np.int8)
    measurement_noise = rng.normal(size=(n, horizon))
    process_noise = rng.normal(0.0, 0.01, size=(n, horizon))
    position = rng.uniform(-4.0, 4.0, size=n)
    goal = rng.choice(np.asarray([-3.0, 3.0]), size=n)
    mode = np.zeros(n, dtype=np.int8)
    for t in range(horizon):
        goal[rng.random(n) < hazard] *= -1.0
        previous_mode = mode.copy()
        mode[(previous_mode == 0) & (rng.random(n) < FORWARD_TO_REVERSAL)] = 1
        mode[(previous_mode == 1) & (rng.random(n) < REVERSAL_TO_FORWARD)] = 0
        goals[:, t] = goal
        modes[:, t] = mode
    return Exogenous(goals, modes, measurement_noise, process_noise, position)


def make_training_data(exogenous: Exogenous, sigma_f: float, sigma_r: float) -> tuple[np.ndarray, np.ndarray]:
    n, horizon = exogenous.goals.shape
    position = exogenous.initial_position.copy()
    previous_action = np.zeros(n, dtype=np.float64)
    inputs = np.empty((n, horizon, 3), dtype=np.float32)
    labels = np.empty((n, horizon, 1), dtype=np.float32)
    for t in range(horizon):
        error = exogenous.goals[:, t] - position
        sigma = np.where(exogenous.modes[:, t] == 0, sigma_f, sigma_r)
        observation = error + sigma * exogenous.measurement_noise[:, t]
        mode_code = np.where(exogenous.modes[:, t] == 0, 1.0, -1.0)
        inputs[:, t, 0] = observation / 5.0
        inputs[:, t, 1] = mode_code
        inputs[:, t, 2] = previous_action
        action = np.tanh(0.7 * error)
        labels[:, t, 0] = action
        position = np.clip(position + 0.15 * action + exogenous.process_noise[:, t], -5.0, 5.0)
        previous_action = action
    return inputs, labels


def train_gru(seed: int) -> tuple[ActionGRU, dict[str, float | int]]:
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    rng = np.random.default_rng(seed)
    exogenous = sample_exogenous(rng, TRAIN_EPISODES, TRAIN_HORIZON, hazard=0.01)
    inputs_np, labels_np = make_training_data(exogenous, sigma_f=0.2, sigma_r=1.2)
    inputs = torch.from_numpy(inputs_np)
    labels = torch.from_numpy(labels_np)
    model = ActionGRU(hidden=16)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
    losses: list[float] = []
    for _ in range(8):
        order = torch.randperm(TRAIN_EPISODES)
        epoch_loss = 0.0
        batches = 0
        for start in range(0, TRAIN_EPISODES, 32):
            indexes = order[start : start + 32]
            prediction = model(inputs[indexes])
            loss = torch.mean((prediction - labels[indexes]) ** 2)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.detach())
            batches += 1
        losses.append(epoch_loss / batches)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    return model.eval(), {
        "parameters": parameter_count,
        "first_epoch_mse": losses[0],
        "last_epoch_mse": losses[-1],
        "epochs": len(losses),
        "training_episodes": TRAIN_EPISODES,
        "training_horizon": TRAIN_HORIZON,
    }


def rollout(
    exogenous: Exogenous,
    sigma_f: float,
    sigma_r: float,
    policy: str,
    model: ActionGRU | None = None,
) -> dict[str, np.ndarray]:
    n, horizon = exogenous.goals.shape
    position = exogenous.initial_position.copy()
    previous_action = np.zeros(n, dtype=np.float64)
    hidden: torch.Tensor | None = None
    absolute_error = np.empty((n, horizon), dtype=np.float64)
    signed_error = np.empty((n, horizon), dtype=np.float64)
    inside_target = np.empty((n, horizon), dtype=np.float64)
    actions = np.empty((n, horizon), dtype=np.float64)

    for t in range(horizon):
        error = exogenous.goals[:, t] - position
        sigma = np.where(exogenous.modes[:, t] == 0, sigma_f, sigma_r)
        observation = error + sigma * exogenous.measurement_noise[:, t]
        q = exogenous.modes[:, t]
        if policy == "GATED_FEEDBACK":
            gain = np.where(q == 0, SENSORY_GAIN_FORWARD, SENSORY_GAIN_REVERSAL)
            action = np.tanh(0.6 * (gain * observation + ACTION_FEEDBACK * previous_action))
        elif policy == "NO_GATE_FEEDBACK":
            action = np.tanh(0.6 * (NO_GATE_GAIN * observation + ACTION_FEEDBACK * previous_action))
        elif policy == "GATED_NO_FEEDBACK":
            gain = np.where(q == 0, SENSORY_GAIN_FORWARD, SENSORY_GAIN_REVERSAL)
            action = np.tanh(0.6 * gain * observation)
        elif policy == "UNGATED_MEMORYLESS":
            action = np.tanh(0.6 * observation)
        elif policy == "TRAINED_GRU":
            assert model is not None
            mode_code = np.where(q == 0, 1.0, -1.0)
            model_input = np.column_stack([observation / 5.0, mode_code, previous_action]).astype(np.float32)
            with torch.no_grad():
                state, hidden = model.gru(torch.from_numpy(model_input[:, None, :]), hidden)
                action = torch.tanh(model.readout(state[:, 0, :])).squeeze(1).numpy().astype(np.float64)
        elif policy == "PRIVILEGED_TEACHER":
            action = np.tanh(0.7 * error)
        else:
            raise ValueError(policy)

        absolute_error[:, t] = np.abs(error)
        signed_error[:, t] = error
        inside_target[:, t] = (np.abs(error) < 0.5).astype(np.float64)
        actions[:, t] = action
        position = np.clip(position + 0.15 * action + exogenous.process_noise[:, t], -5.0, 5.0)
        previous_action = action

    # Direction-correction latency after a goal switch, requiring 3 consecutive
    # movement commands in the new target direction; no-switch episodes are NA.
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
    latency = np.asarray(
        [float(np.mean(values)) if values else np.nan for values in switch_delays], dtype=np.float64
    )
    return {
        "mean_absolute_error": absolute_error.mean(axis=1),
        "target_zone_fraction": inside_target.mean(axis=1),
        "direction_switch_delay": latency,
        "action": actions,
    }


def bootstrap_interval(values: np.ndarray, rng: np.random.Generator) -> list[float]:
    finite = values[np.isfinite(values)]
    indexes = rng.integers(0, len(finite), size=(BOOTSTRAPS, len(finite)))
    low, high = np.quantile(finite[indexes].mean(axis=1), [0.025, 0.975])
    return [float(low), float(high)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    model, train_info = train_gru(MASTER_SEED + 1)
    seed_children = iter(np.random.SeedSequence(MASTER_SEED).spawn(len(HAZARDS) * len(NOISE_PROFILES)))
    rows: list[dict[str, float | int | str]] = []
    summaries = []
    bootstrap_rng = np.random.default_rng(MASTER_SEED + 2)
    policy_names = (
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
                np.random.default_rng(next(seed_children)), TEST_EPISODES, HORIZON, hazard
            )
            values: dict[str, dict[str, np.ndarray]] = {}
            for policy in policy_names:
                values[policy] = rollout(
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
                            "mean_absolute_error": float(values[policy]["mean_absolute_error"][episode]),
                            "target_zone_fraction": float(values[policy]["target_zone_fraction"][episode]),
                            "direction_switch_delay": float(values[policy]["direction_switch_delay"][episode]),
                        }
                    )
            for policy, result in values.items():
                summaries.append(
                    {
                        "hazard": hazard,
                        "noise_profile": profile,
                        "sigma_forward": sigma_f,
                        "sigma_reversal": sigma_r,
                        "policy": policy,
                        "mean_absolute_error": float(result["mean_absolute_error"].mean()),
                        "mean_target_zone_fraction": float(result["target_zone_fraction"].mean()),
                        "mean_direction_switch_delay": float(np.nanmean(result["direction_switch_delay"])),
                        "episodes": TEST_EPISODES,
                    }
                )
            for baseline in ("NO_GATE_FEEDBACK", "GATED_NO_FEEDBACK", "UNGATED_MEMORYLESS", "TRAINED_GRU", "PRIVILEGED_TEACHER"):
                for metric in ("mean_absolute_error", "target_zone_fraction"):
                    delta = values["GATED_FEEDBACK"][metric] - values[baseline][metric]
                    summaries.append(
                        {
                            "hazard": hazard,
                            "noise_profile": profile,
                            "sigma_forward": sigma_f,
                            "sigma_reversal": sigma_r,
                            "policy": f"PAIRED_GATED_MINUS_{baseline}",
                            "metric": metric,
                            "mean_difference": float(delta.mean()),
                            "paired_episode_bootstrap_95ci": bootstrap_interval(delta, bootstrap_rng),
                            "episodes": TEST_EPISODES,
                        }
                    )

    csv_path = OUT / "episode_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "condition_summary.json").write_text(
        json.dumps(summaries, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "EXPLORATORY_CLOSED_LOOP_CONTROL_EXPERIMENT",
                "master_seed": MASTER_SEED,
                "horizon": HORIZON,
                "test_episodes_per_cell": TEST_EPISODES,
                "hazards": HAZARDS,
                "noise_profiles": NOISE_PROFILES,
                "mode_transition": {"forward_to_reversal": FORWARD_TO_REVERSAL, "reversal_to_forward": REVERSAL_TO_FORWARD},
                "plant": {"position_bounds": [-5, 5], "action_gain": 0.15, "process_noise_sd": 0.01},
                "independent_unit": "episode",
                "trained_gru": train_info,
                "policies": policy_names,
                "outputs": [csv_path.name, "condition_summary.json"],
                "limitations": ["mode-dependent noise is synthetic, not established by source biology", "privileged teacher sees true state", "no biological measurements used"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
