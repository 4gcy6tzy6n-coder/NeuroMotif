#!/usr/bin/env python3
"""Outcome-informed direct-utility optimization for a mode-dependent gain."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "results" / "M2_TARGETED_GAIN_OPTIMIZATION"
MASTER_SEED = 20260930
TRAIN_SEEDS = tuple(range(10))
TRAIN_STEPS = 200
TRAIN_BATCH = 64
TRAIN_HORIZON = 160
TEST_EPISODES = 500
TEST_HORIZON = 240
TEST_HAZARDS = (0.005, 0.04)
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
POLICIES = ("LEARNED_MODE_GAIN", "LEARNED_GENERIC_CONTEXT", "FIXED_GATED", "FIXED_NO_GATE")


@dataclass
class Exogenous:
    goals: np.ndarray
    modes: np.ndarray
    measurement_noise: np.ndarray
    process_noise: np.ndarray
    initial_position: np.ndarray
    hazard: np.ndarray


def inverse_softplus(value: float) -> float:
    return float(np.log(np.expm1(value)))


def sample_exogenous(
    rng: np.random.Generator,
    n: int,
    horizon: int,
    *,
    hazard: float | None = None,
) -> Exogenous:
    hazards = (
        np.full(n, hazard, dtype=np.float64)
        if hazard is not None
        else np.exp(rng.uniform(np.log(0.002), np.log(0.08), size=n))
    )
    goals = np.empty((n, horizon), dtype=np.float32)
    modes = np.empty((n, horizon), dtype=np.int8)
    measurement_noise = rng.normal(size=(n, horizon)).astype(np.float32)
    process_noise = rng.normal(0.0, 0.01, size=(n, horizon)).astype(np.float32)
    position = rng.uniform(-4.0, 4.0, size=n).astype(np.float32)
    goal = rng.choice(np.asarray([-3.0, 3.0]), size=n).astype(np.float32)
    mode = np.zeros(n, dtype=np.int8)
    for t in range(horizon):
        goal[rng.random(n) < hazards] *= -1.0
        prev_mode = mode.copy()
        mode[(prev_mode == 0) & (rng.random(n) < F2R)] = 1
        mode[(prev_mode == 1) & (rng.random(n) < R2F)] = 0
        goals[:, t] = goal
        modes[:, t] = mode
    return Exogenous(goals, modes, measurement_noise, process_noise, position, hazards)


def tensor_mae(raw: torch.Tensor, exo: Exogenous, family: str) -> torch.Tensor:
    goals = torch.from_numpy(exo.goals)
    modes = torch.from_numpy(exo.modes.astype(np.float32))
    measurement_noise = torch.from_numpy(exo.measurement_noise)
    process_noise = torch.from_numpy(exo.process_noise)
    position = torch.from_numpy(exo.initial_position.copy())
    previous_action = torch.zeros_like(position)
    total_error = torch.zeros_like(position)

    if family == "mode_gain":
        gain_forward, gain_reversal, action_feedback = F.softplus(raw)
    elif family == "generic_context":
        sensory_gain, action_feedback = F.softplus(raw[:2])
        mode_bias = raw[2]
    else:
        raise ValueError(family)

    for t in range(goals.shape[1]):
        error = goals[:, t] - position
        sigma = torch.where(modes[:, t] == 0, 0.2, 1.2)
        observation = error + sigma * measurement_noise[:, t]
        if family == "mode_gain":
            gain = torch.where(modes[:, t] == 0, gain_forward, gain_reversal)
            preactivation = gain * (observation / 5.0) + action_feedback * previous_action
        else:
            mode_code = torch.where(modes[:, t] == 0, 1.0, -1.0)
            preactivation = sensory_gain * (observation / 5.0) + action_feedback * previous_action + mode_bias * mode_code
        action = torch.tanh(preactivation)
        total_error = total_error + torch.abs(error)
        position = torch.clamp(position + 0.15 * action + process_noise[:, t], -5.0, 5.0)
        previous_action = action
    return (total_error / goals.shape[1]).mean()


def train(seed: int, family: str) -> dict[str, object]:
    if family == "mode_gain":
        initial = [inverse_softplus(3.0), inverse_softplus(0.45), inverse_softplus(0.12)]
    else:
        initial = [inverse_softplus(GAIN_NO_GATE * 3.0), inverse_softplus(0.12), 0.0]
    raw = torch.nn.Parameter(torch.tensor(initial, dtype=torch.float32))
    optimizer = torch.optim.Adam([raw], lr=0.01)
    loss_start: list[float] = []
    loss_end: list[float] = []
    for step in range(TRAIN_STEPS):
        # Same exogenous batch is regenerated for the paired family at each
        # seed/update, giving common random numbers during the comparison.
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, seed, step, 4242]))
        exo = sample_exogenous(rng, TRAIN_BATCH, TRAIN_HORIZON)
        loss = tensor_mae(raw, exo, family)
        if step < 20:
            loss_start.append(float(loss.detach()))
        if step >= TRAIN_STEPS - 20:
            loss_end.append(float(loss.detach()))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    if family == "mode_gain":
        fitted = F.softplus(raw).detach().numpy().tolist()
        parameters = {"gain_forward": float(fitted[0]), "gain_reversal": float(fitted[1]), "action_feedback": float(fitted[2])}
    else:
        parameters = {
            "sensory_gain": float(F.softplus(raw[0]).detach()),
            "action_feedback": float(F.softplus(raw[1]).detach()),
            "mode_bias": float(raw[2].detach()),
        }
    return {
        "parameters": parameters,
        "trainable_parameter_count": 3,
        "initial_20_update_mean_training_mae": float(np.mean(loss_start)),
        "final_20_update_mean_training_mae": float(np.mean(loss_end)),
        "training_steps": TRAIN_STEPS,
        "training_batch_size": TRAIN_BATCH,
    }


def rollout(
    exo: Exogenous,
    controller: str,
    fitted: dict[str, float] | None = None,
    *,
    sigma_forward: float,
    sigma_reversal: float,
) -> dict[str, np.ndarray]:
    n, horizon = exo.goals.shape
    position = exo.initial_position.copy()
    previous_action = np.zeros(n, dtype=np.float64)
    abs_error = np.empty((n, horizon), dtype=np.float64)
    signed_error = np.empty((n, horizon), dtype=np.float64)
    in_target = np.empty((n, horizon), dtype=np.float64)
    actions = np.empty((n, horizon), dtype=np.float64)
    for t in range(horizon):
        error = exo.goals[:, t] - position
        mode = exo.modes[:, t]
        sigma = np.where(mode == 0, sigma_forward, sigma_reversal)
        observation = error + sigma * exo.measurement_noise[:, t]
        if controller == "LEARNED_MODE_GAIN":
            gain = np.where(mode == 0, fitted["gain_forward"], fitted["gain_reversal"])
            action = np.tanh(gain * observation / 5.0 + fitted["action_feedback"] * previous_action)
        elif controller == "LEARNED_GENERIC_CONTEXT":
            mode_code = np.where(mode == 0, 1.0, -1.0)
            action = np.tanh(fitted["sensory_gain"] * observation / 5.0 + fitted["action_feedback"] * previous_action + fitted["mode_bias"] * mode_code)
        elif controller == "FIXED_GATED":
            gain = np.where(mode == 0, 3.0, 0.45)
            action = np.tanh(gain * observation / 5.0 + 0.12 * previous_action)
        elif controller == "FIXED_NO_GATE":
            action = np.tanh(GAIN_NO_GATE * 3.0 * observation / 5.0 + 0.12 * previous_action)
        else:
            raise ValueError(controller)
        abs_error[:, t] = np.abs(error)
        signed_error[:, t] = error
        in_target[:, t] = (np.abs(error) < 0.5).astype(np.float64)
        actions[:, t] = action
        position = np.clip(position + 0.15 * action + exo.process_noise[:, t], -5.0, 5.0)
        previous_action = action
    delays: list[list[float]] = [[] for _ in range(n)]
    for t in range(1, horizon):
        switched = exo.goals[:, t] != exo.goals[:, t - 1]
        for ep in np.flatnonzero(switched):
            end = min(horizon - 3, t + 39)
            delay = 40.0
            for candidate in range(t, end + 1):
                if np.all(actions[ep, candidate:candidate+3] * signed_error[ep, candidate:candidate+3] > 0):
                    delay = float(candidate - t)
                    break
            delays[ep].append(delay)
    return {
        "mean_absolute_error": abs_error.mean(axis=1),
        "target_zone_fraction": in_target.mean(axis=1),
        "direction_switch_delay": np.asarray([np.mean(x) if x else np.nan for x in delays]),
    }


def crossed_ci(differences: np.ndarray, seed: int) -> list[float]:
    # axes: training seed × environment cell × shared episode identity
    rng = np.random.default_rng(seed)
    n_seed, n_cell, n_episode = differences.shape
    draws = np.empty(20_000, dtype=np.float64)
    for start in range(0, len(draws), 100):
        b = min(100, len(draws) - start)
        seed_idx = rng.integers(0, n_seed, size=(b, n_seed))
        episode_idx = rng.integers(0, n_episode, size=(b, n_cell, n_episode))
        selected = differences[seed_idx]
        indexes = np.broadcast_to(episode_idx[:, None, :, :], selected.shape)
        draws[start:start+b] = np.take_along_axis(selected, indexes, axis=3).mean(axis=(1, 2, 3))
    return [float(x) for x in np.quantile(draws, [0.025, 0.975])]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(1)
    models: list[dict[str, object]] = []
    rows: list[dict[str, object]] = []
    primary_diffs = np.empty((len(TRAIN_SEEDS), len(TEST_HAZARDS), TEST_EPISODES), dtype=np.float64)
    train_records = []

    for seed_i, train_seed in enumerate(TRAIN_SEEDS):
        gate_model = train(train_seed, "mode_gain")
        generic_model = train(train_seed, "generic_context")
        train_records.append({"train_seed": train_seed, "mode_gain": gate_model, "generic_context": generic_model})
        models.append({"train_seed": train_seed, "mode_gain": gate_model["parameters"], "generic_context": generic_model["parameters"]})
        for hazard_i, hazard in enumerate(TEST_HAZARDS):
            for profile_i, (profile, (sigma_f, sigma_r)) in enumerate(NOISE_PROFILES.items()):
                rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, 9900, hazard_i, profile_i]))
                exo = sample_exogenous(rng, TEST_EPISODES, TEST_HORIZON, hazard=hazard)
                outputs = {
                    "LEARNED_MODE_GAIN": rollout(exo, "LEARNED_MODE_GAIN", gate_model["parameters"], sigma_forward=sigma_f, sigma_reversal=sigma_r),
                    "LEARNED_GENERIC_CONTEXT": rollout(exo, "LEARNED_GENERIC_CONTEXT", generic_model["parameters"], sigma_forward=sigma_f, sigma_reversal=sigma_r),
                    "FIXED_GATED": rollout(exo, "FIXED_GATED", sigma_forward=sigma_f, sigma_reversal=sigma_r),
                    "FIXED_NO_GATE": rollout(exo, "FIXED_NO_GATE", sigma_forward=sigma_f, sigma_reversal=sigma_r),
                }
                difference = outputs["LEARNED_MODE_GAIN"]["mean_absolute_error"] - outputs["LEARNED_GENERIC_CONTEXT"]["mean_absolute_error"]
                if profile == "HIGH_REVERSAL_NOISE":
                    primary_diffs[seed_i, hazard_i] = difference
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

    primary_mean = float(primary_diffs.mean())
    primary_ci = crossed_ci(primary_diffs, MASTER_SEED + 77)
    per_cell = []
    for hazard_i, hazard in enumerate(TEST_HAZARDS):
        per_cell.append(
            {
                "hazard": hazard,
                "profile": "HIGH_REVERSAL_NOISE",
                "mean_paired_mae_difference_mode_gain_minus_generic": float(primary_diffs[:, hazard_i].mean()),
            }
        )
    out_csv = OUT / "episode_metrics.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "status": "POST_RESULT_TARGETED_OPTIMIZATION_COMPLETE",
        "primary_estimand": "equal-hazard mean paired episode MAE difference (LEARNED_MODE_GAIN - LEARNED_GENERIC_CONTEXT) under high-reversal-noise profile",
        "primary_mean_difference": primary_mean,
        "crossed_hierarchical_95ci": primary_ci,
        "interpretation": "MODE_GAIN_LOWER_ERROR" if primary_ci[1] < 0 else "MODE_GAIN_HIGHER_ERROR" if primary_ci[0] > 0 else "INCONCLUSIVE_INTERVAL_INCLUDES_ZERO",
        "per_hazard_primary_cells": per_cell,
        "secondary_profiles_are_descriptive_only": ["EQUAL_NOISE", "REVERSED_NOISE"],
        "training_seeds": len(TRAIN_SEEDS),
        "test_episodes_per_seed_cell": TEST_EPISODES,
        "note": "Outcome-informed engineering exploration; no biological validation or broad task-family claim.",
    }
    (OUT / "primary_result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "experiment": "M2_TARGETED_GAIN_OPTIMIZATION",
        "seed": MASTER_SEED,
        "training_seeds": train_records,
        "training": {"steps": TRAIN_STEPS, "batch_size": TRAIN_BATCH, "horizon": TRAIN_HORIZON, "direct_objective": "mean episode MAE", "task_distribution": "hazard log-uniform [0.002,0.08], sigma_F=0.2, sigma_R=1.2"},
        "test": {"hazards": TEST_HAZARDS, "profiles": NOISE_PROFILES, "episodes_per_cell_per_seed": TEST_EPISODES, "horizon": TEST_HORIZON, "common_random_numbers": True},
        "independent_unit": "training seed and shared test episode identity as crossed factors",
        "policies": list(POLICIES),
        "outputs": ["episode_metrics.csv", "primary_result.json"],
        "warning": "post-result targeted engineering study, not confirmation or biological-to-AI transfer",
    }
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"primary_mean_difference": primary_mean, "ci95": primary_ci, "interpretation": result["interpretation"], "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
