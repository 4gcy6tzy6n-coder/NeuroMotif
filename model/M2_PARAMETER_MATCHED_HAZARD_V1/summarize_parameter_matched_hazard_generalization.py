#!/usr/bin/env python3
"""Schema-check and report the frozen M2 scalar-controller follow-up outputs."""

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
BOOTSTRAPS = 20_000
EXPECTED_SEEDS = set(range(10))
EXPECTED_HAZARDS = (0.005, 0.04)
EXPECTED_PROFILES = ("HIGH_REVERSAL_NOISE", "EQUAL_NOISE", "REVERSED_NOISE")
EXPECTED_POLICIES = ("FIXED_GATED", "FIXED_NO_GATE", "LEARNED_GATED", "LEARNED_NO_GATE", "PRIVILEGED_TEACHER")
METRIC = "mean_absolute_error"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def cell_bootstrap(values: np.ndarray, rng: np.random.Generator) -> list[float]:
    """Hierarchical resample of train seeds, then paired episodes within seed."""
    n_seeds, n_episodes = values.shape
    draws = np.empty(BOOTSTRAPS, dtype=np.float64)
    batch = 200
    for start in range(0, BOOTSTRAPS, batch):
        size = min(batch, BOOTSTRAPS - start)
        seed_idx = rng.integers(0, n_seeds, size=(size, n_seeds))
        selected = values[seed_idx]
        episode_idx = rng.integers(0, n_episodes, size=(size, n_seeds, n_episodes))
        draws[start : start + size] = np.take_along_axis(selected, episode_idx, axis=2).mean(axis=(1, 2))
    return [float(x) for x in np.quantile(draws, [0.025, 0.975])]


def main() -> None:
    summary = json.loads((OUT / "primary_result.json").read_text(encoding="utf-8"))
    manifest = json.loads((OUT / "run_manifest.json").read_text(encoding="utf-8"))
    records: dict[tuple[int, float, str, int], dict[str, dict[str, float]]] = defaultdict(dict)
    with (OUT / "episode_metrics.csv").open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        required = {
            "train_seed", "hazard", "noise_profile", "episode", "policy",
            "mean_absolute_error", "target_zone_fraction", "direction_switch_delay",
        }
        if set(reader.fieldnames or ()) != required | {"sigma_forward", "sigma_reversal"}:
            raise RuntimeError(f"unexpected CSV schema: {reader.fieldnames}")
        for row in reader:
            key = (int(row["train_seed"]), float(row["hazard"]), row["noise_profile"], int(row["episode"]))
            policy = row["policy"]
            if policy in records[key]:
                raise RuntimeError(f"duplicate policy row: {key}, {policy}")
            records[key][policy] = {
                "mean_absolute_error": float(row["mean_absolute_error"]),
                "target_zone_fraction": float(row["target_zone_fraction"]),
                "direction_switch_delay": float(row["direction_switch_delay"]) if row["direction_switch_delay"] else float("nan"),
            }

    expected_keys = {
        (seed, hazard, profile, episode)
        for seed in EXPECTED_SEEDS
        for hazard in EXPECTED_HAZARDS
        for profile in EXPECTED_PROFILES
        for episode in range(300)
    }
    if set(records) != expected_keys:
        raise RuntimeError(f"test-cell key mismatch: expected {len(expected_keys)}, observed {len(records)}")
    for key, policies in records.items():
        if set(policies) != set(EXPECTED_POLICIES):
            raise RuntimeError(f"policy pairing incomplete for {key}: {sorted(policies)}")
    if len(records) * len(EXPECTED_POLICIES) != 90_000:
        raise RuntimeError("unexpected episode-row count")
    if set(manifest["training"]["independent_training_seeds"]) != EXPECTED_SEEDS:
        raise RuntimeError("training-seed manifest mismatch")
    for seed_record in manifest["training"]["controllers"]:
        if len(seed_record["learned_gated"]["weights"]) != 2 or len(seed_record["learned_no_gate"]["weights"]) != 2:
            raise RuntimeError("learned controller parameter count differs from the contract")

    cell_keys = [(hazard, profile) for hazard in EXPECTED_HAZARDS for profile in EXPECTED_PROFILES]
    differences = np.empty((len(EXPECTED_SEEDS), len(cell_keys), 300), dtype=np.float64)
    seed_order = sorted(EXPECTED_SEEDS)
    cell_rows = []
    for seed_i, seed in enumerate(seed_order):
        for cell_i, (hazard, profile) in enumerate(cell_keys):
            diffs = []
            for episode in range(300):
                entry = records[(seed, hazard, profile, episode)]
                diffs.append(entry["LEARNED_GATED"][METRIC] - entry["LEARNED_NO_GATE"][METRIC])
            differences[seed_i, cell_i] = diffs

    raw_primary_mean = float(differences.mean())
    if not np.isclose(raw_primary_mean, summary["primary_mean_difference"], rtol=0, atol=1e-12):
        raise RuntimeError(f"primary estimate mismatch: {raw_primary_mean} vs {summary['primary_mean_difference']}")
    ci_rng = np.random.default_rng(20260930 + 991)
    report_cells = []
    for cell_i, (hazard, profile) in enumerate(cell_keys):
        per_seed_episode = differences[:, cell_i, :]
        ci = cell_bootstrap(per_seed_episode, ci_rng)
        report_cells.append(
            {
                "hazard": hazard,
                "noise_profile": profile,
                "mean_paired_difference": float(per_seed_episode.mean()),
                "hierarchical_bootstrap_95ci": ci,
                "episodes_per_training_seed": 300,
                "training_seeds": 10,
            }
        )

    summary["cell_descriptive_contrasts"] = report_cells
    (OUT / "primary_result.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# M2 parameter-matched hazard-generalization follow-up",
        "",
        "**Status:** `POST_RESULT_EXPLORATORY_COMPLETE`; not biological validation or confirmatory transfer.",
        "",
        "## Primary result",
        "",
        "The pre-specified primary contrast was episode MAE for `LEARNED_GATED − LEARNED_NO_GATE`, averaged equally across six environment cells and ten training seeds. Negative values favor gating.",
        "",
        f"- Mean paired difference: `{raw_primary_mean:+.5f}` MAE.",
        f"- 95% hierarchical bootstrap interval: `[{summary['primary_hierarchical_bootstrap_95ci'][0]:+.5f}, {summary['primary_hierarchical_bootstrap_95ci'][1]:+.5f}]`.",
        f"- Frozen interpretation: `{summary['primary_interpretation']}`.",
        "- The interval is above zero: in this simulator and held-out hazard grid, the parameter-matched learned gated controller had higher (worse) mean target error than the learned no-gate controller.",
        "",
        "## Descriptive cell results",
        "",
        "| Hazard | Noise profile | Gated − no-gate MAE | 95% hierarchical interval |",
        "|---:|---|---:|---:|",
    ]
    for item in report_cells:
        lines.append(
            f"| {item['hazard']:.3f} | {item['noise_profile']} | {item['mean_paired_difference']:+.5f} | "
            f"[{item['hierarchical_bootstrap_95ci'][0]:+.5f}, {item['hierarchical_bootstrap_95ci'][1]:+.5f}] |"
        )
    lines.extend(
        [
            "",
            "## Scope and limitations",
            "",
            "- Both learned policies have exactly two trainable scalar parameters and used matched training sizes, seeds, DAgger rounds, and optimizer settings.",
            "- The ten independent training seeds and 300 paired episodes per cell are represented in the hierarchical intervals; frames and time steps were not treated as independent samples.",
            "- Test hazards (0.005 and 0.04) were not used as fixed training conditions. The three sensory-noise profile values were already present in prior M2 experiments, so only the hazard values are new holdouts.",
            "- The privileged teacher is an oracle reference. The result does not compare against GRU/RNN families, establish generalization to other task generators, or validate the synthetic state/noise relationship as biology.",
            "- This analysis was informed by prior M2 outcomes and remains exploratory even though the hazard values were held out.",
            "",
            "## Provenance",
            "",
            "Contract and preflight hashes are recorded in `M2_PARAMETER_MATCHED_HAZARD_GENERALIZATION_PREFLIGHT.json`. Episode rows and training seeds are in `episode_metrics.csv` and `run_manifest.json`.",
        ]
    )
    results_path = OUT / "RESULTS.md"
    results_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    postrun = {
        "status": "SCHEMA_AND_PRIMARY_ESTIMATE_VERIFIED",
        "rows": len(records) * len(EXPECTED_POLICIES),
        "paired_keys": len(records),
        "policies_per_key": len(EXPECTED_POLICIES),
        "primary_mean_recomputed": raw_primary_mean,
        "primary_mean_matches_primary_result": True,
        "files": {
            "episode_metrics.csv": digest(OUT / "episode_metrics.csv"),
            "primary_result.json": digest(OUT / "primary_result.json"),
            "run_manifest.json": digest(OUT / "run_manifest.json"),
            "RESULTS.md": digest(results_path),
        },
    }
    (OUT / "POSTRUN_SCHEMA_VERIFICATION.json").write_text(json.dumps(postrun, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(postrun, indent=2))


if __name__ == "__main__":
    main()
