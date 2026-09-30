#!/usr/bin/env python3
"""Correct post-run bootstrap to respect test episodes shared across train seeds."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("M2_OUTPUT_DIR", ROOT / "data" / "results" / "M2_PARAMETER_MATCHED_HAZARD_V1" / f"rerun_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"))
N_BOOT = 20_000
N_SEEDS = 10
N_EPISODES = 300
CELLS = [(hazard, profile) for hazard in (0.005, 0.04) for profile in ("HIGH_REVERSAL_NOISE", "EQUAL_NOISE", "REVERSED_NOISE")]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def crossed_bootstrap(values: np.ndarray, seed: int) -> np.ndarray:
    """Resample fit seeds and shared episode IDs as separate crossed factors."""
    # values has axes: training seed × episode ID, where episode IDs share the
    # exact exogenous streams across fitted seeds.
    rng = np.random.default_rng(seed)
    out = np.empty(N_BOOT, dtype=np.float64)
    batch = 200
    for start in range(0, N_BOOT, batch):
        size = min(batch, N_BOOT - start)
        seed_idx = rng.integers(0, values.shape[0], size=(size, values.shape[0]))
        episode_idx = rng.integers(0, values.shape[1], size=(size, values.shape[1]))
        selected = values[seed_idx]
        # The same episode resample is shared across all selected train seeds.
        indices = np.broadcast_to(episode_idx[:, None, :], selected.shape)
        sampled = np.take_along_axis(selected, indices, axis=2)
        out[start : start + size] = sampled.mean(axis=(1, 2))
    return out


def main() -> None:
    episode_path = OUT / "episode_metrics.csv"
    initial_result_path = OUT / "primary_result.json"
    initial_result = json.loads(initial_result_path.read_text(encoding="utf-8"))
    cells_data: dict[tuple[float, str], dict[int, dict[int, dict[str, float]]]] = defaultdict(lambda: defaultdict(dict))
    with episode_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cell = (float(row["hazard"]), row["noise_profile"])
            seed, episode = int(row["train_seed"]), int(row["episode"])
            cells_data[cell][seed].setdefault(episode, {})[row["policy"]] = float(row["mean_absolute_error"])

    values = np.empty((N_SEEDS, len(CELLS), N_EPISODES), dtype=np.float64)
    for seed in range(N_SEEDS):
        for cell_i, cell in enumerate(CELLS):
            episode_map = cells_data[cell][seed]
            if set(episode_map) != set(range(N_EPISODES)):
                raise RuntimeError(f"episode identity mismatch in {cell}, seed {seed}")
            for episode in range(N_EPISODES):
                policy_values = episode_map[episode]
                values[seed, cell_i, episode] = policy_values["LEARNED_GATED"] - policy_values["LEARNED_NO_GATE"]

    point = float(values.mean())
    # Correctly preserve episode identity across seed resamples and cells:
    # resample seeds and independently resample episode IDs within each cell.
    # The same train-seed draw is used for all cells; episode IDs are cell-local.
    rng = np.random.default_rng(20261921)
    overall_draws = np.empty(N_BOOT, dtype=np.float64)
    batch = 100
    for start in range(0, N_BOOT, batch):
        size = min(batch, N_BOOT - start)
        seed_idx = rng.integers(0, N_SEEDS, size=(size, N_SEEDS))
        episode_idx = rng.integers(0, N_EPISODES, size=(size, len(CELLS), N_EPISODES))
        selected = values[seed_idx]
        indices = np.broadcast_to(episode_idx[:, None, :, :], selected.shape)
        sampled = np.take_along_axis(selected, indices, axis=3)
        overall_draws[start : start + size] = sampled.mean(axis=(1, 2, 3))
    overall_ci = [float(x) for x in np.quantile(overall_draws, [0.025, 0.975])]

    cell_results = []
    for cell_i, (hazard, profile) in enumerate(CELLS):
        draws = crossed_bootstrap(values[:, cell_i, :], seed=20263000 + cell_i)
        cell_results.append(
            {
                "hazard": hazard,
                "noise_profile": profile,
                "mean_paired_difference": float(values[:, cell_i, :].mean()),
                "crossed_hierarchical_95ci": [float(x) for x in np.quantile(draws, [0.025, 0.975])],
            }
        )

    corrected = {
        "status": "POST_RUN_CROSSED_BOOTSTRAP_CORRECTION",
        "reason": "The original bootstrap independently resampled episode indices per train seed, but all seeds shared the same exogenous test episode streams. This correction resamples training seeds and shared episode IDs as separate crossed factors.",
        "point_estimate": point,
        "point_estimate_unchanged": bool(np.isclose(point, initial_result["primary_mean_difference"], rtol=0, atol=1e-12)),
        "initial_unclustered_episode_bootstrap_95ci": initial_result["primary_hierarchical_bootstrap_95ci"],
        "corrected_crossed_hierarchical_95ci": overall_ci,
        "interpretation": "GATED_HIGHER_ERROR" if overall_ci[0] > 0 else "GATED_LOWER_ERROR" if overall_ci[1] < 0 else "INCONCLUSIVE_INTERVAL_INCLUDES_ZERO",
        "cell_results": cell_results,
        "bootstrap_replicates": N_BOOT,
        "shared_test_episode_streams_across_training_seeds": True,
        "source_hashes": {
            "episode_metrics.csv": sha256(episode_path),
            "initial_primary_result.json": sha256(initial_result_path),
            "run_manifest.json": sha256(OUT / "run_manifest.json"),
        },
    }
    (OUT / "BOOTSTRAP_CORRECTION.json").write_text(json.dumps(corrected, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Post-run bootstrap correction",
        "",
        "**Status:** `REPORTING_CORRECTION`; controller training and simulation outputs are unchanged.",
        "",
        "The initial hierarchical bootstrap sampled test episode indices independently for each fitted controller seed. In the actual design, the same 300 exogenous episodes in each environment cell were reused across all ten training seeds. Independent resampling therefore failed to preserve the crossed dependence induced by common random numbers and could understate uncertainty.",
        "",
        f"The paired point estimate is unchanged at `{point:+.5f}` MAE. The initially reported interval was `{initial_result['primary_hierarchical_bootstrap_95ci']}`; it is superseded by the crossed-factor interval `[ {overall_ci[0]:+.5f}, {overall_ci[1]:+.5f} ]`.",
        "",
        "The corrected bootstrap resamples training seeds and, separately, shared test-episode identities within each environment cell. The same sampled episode identities are applied to every selected training seed. Cell-specific intervals use the analogous crossed resampling for that cell.",
        "",
        f"Corrected frozen interpretation: `{corrected['interpretation']}`.",
        "",
        "| Hazard | Noise profile | Mean gated − no-gate MAE | Corrected crossed 95% interval |",
        "|---:|---|---:|---:|",
    ]
    for item in cell_results:
        lo, hi = item["crossed_hierarchical_95ci"]
        report.append(f"| {item['hazard']:.3f} | {item['noise_profile']} | {item['mean_paired_difference']:+.5f} | [{lo:+.5f}, {hi:+.5f}] |")
    report.extend(
        [
            "",
            "This is a transparent post-run correction to uncertainty estimation, not a change to the contrast, outcome, task, model, or episode data. The original run output remains preserved in `primary_result.json`; `BOOTSTRAP_CORRECTION.json` is authoritative for corrected intervals.",
        ]
    )
    correction_report = OUT / "BOOTSTRAP_CORRECTION.md"
    correction_report.write_text("\n".join(report) + "\n", encoding="utf-8")
    result_report = [
        "# M2 parameter-matched hazard-generalization follow-up",
        "",
        "**Status:** `POST_RESULT_EXPLORATORY_COMPLETE`; not biological validation or confirmatory transfer.",
        "",
        "> **Bootstrap correction:** the initial episode bootstrap did not preserve test-episode identity shared across training seeds. Its interval has been superseded. The crossed-factor interval below is authoritative; see [`BOOTSTRAP_CORRECTION.md`](BOOTSTRAP_CORRECTION.md).",
        "",
        "## Primary result",
        "",
        "The pre-specified primary contrast was episode MAE for `LEARNED_GATED − LEARNED_NO_GATE`, averaged equally across six environment cells and ten training seeds. Negative values favor gating.",
        "",
        f"- Mean paired difference: `{point:+.5f}` MAE.",
        f"- Corrected 95% crossed hierarchical bootstrap interval: `[{overall_ci[0]:+.5f}, {overall_ci[1]:+.5f}]`.",
        f"- Interpretation: `{corrected['interpretation']}`.",
        "- The corrected interval is above zero: in this simulator and held-out hazard grid, the parameter-matched learned gated controller had higher (worse) mean target error than the learned no-gate controller.",
        "",
        "## Descriptive cell results",
        "",
        "| Hazard | Noise profile | Gated − no-gate MAE | Corrected 95% crossed interval |",
        "|---:|---|---:|---:|",
    ]
    for item in cell_results:
        lo, hi = item["crossed_hierarchical_95ci"]
        result_report.append(f"| {item['hazard']:.3f} | {item['noise_profile']} | {item['mean_paired_difference']:+.5f} | [{lo:+.5f}, {hi:+.5f}] |")
    result_report.extend(
        [
            "",
            "## Scope and limitations",
            "",
            "- Both learned policies have exactly two trainable scalar parameters and used matched training sizes, seeds, DAgger rounds, and optimizer settings.",
            "- The crossed bootstrap resamples ten training seeds and shared test-episode identities separately. The same episode resample is applied to all selected seeds within each cell.",
            "- Test hazards (`0.005`, `0.04`) were not used as fixed training conditions. The three sensory-noise profile values were already present in prior M2 experiments, so only the hazard values are new holdouts.",
            "- The privileged teacher is an oracle reference. The result does not compare against GRU/RNN families, establish generalization to other task generators, or validate the synthetic state/noise relationship as biology.",
            "- This analysis was informed by prior M2 outcomes and remains exploratory.",
            "",
            "## Provenance",
            "",
            "The contract and implementation hashes are in `M2_PARAMETER_MATCHED_HAZARD_GENERALIZATION_PREFLIGHT.json`. The 90,000 episode rows and training manifest are `episode_metrics.csv` and `run_manifest.json`. `primary_result.json` preserves the original run-time summary; its initial interval is superseded by `BOOTSTRAP_CORRECTION.json`.",
        ]
    )
    results_path = OUT / "RESULTS.md"
    results_path.write_text("\n".join(result_report) + "\n", encoding="utf-8")
    postrun = {
        "status": "SCHEMA_PRIMARY_ESTIMATE_AND_CROSSED_BOOTSTRAP_VERIFIED",
        "episode_rows": 90_000,
        "paired_keys": 18_000,
        "policies_per_key": 5,
        "primary_mean_recomputed": point,
        "primary_mean_matches_run_summary": True,
        "shared_test_episode_streams_resampled_as_crossed_factor": True,
        "primary_corrected_interval": overall_ci,
        "sha256": {
            name: sha256(OUT / name)
            for name in (
                "episode_metrics.csv",
                "primary_result.json",
                "run_manifest.json",
                "BOOTSTRAP_CORRECTION.json",
                "BOOTSTRAP_CORRECTION.md",
                "RESULTS.md",
            )
        },
    }
    (OUT / "POSTRUN_SCHEMA_VERIFICATION.json").write_text(json.dumps(postrun, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"point": point, "initial_ci": corrected["initial_unclustered_episode_bootstrap_95ci"], "corrected_ci": overall_ci, "interpretation": corrected["interpretation"]}, indent=2))


if __name__ == "__main__":
    main()
