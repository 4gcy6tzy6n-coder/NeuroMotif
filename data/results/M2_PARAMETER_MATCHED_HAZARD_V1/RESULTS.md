# M2 parameter-matched hazard-generalization follow-up

**Status:** `POST_RESULT_EXPLORATORY_COMPLETE`; not biological validation or confirmatory transfer.

> **Bootstrap correction:** the initial episode bootstrap did not preserve test-episode identity shared across training seeds. Its interval has been superseded. The crossed-factor interval below is authoritative; see [`BOOTSTRAP_CORRECTION.md`](BOOTSTRAP_CORRECTION.md).

## Primary result

The pre-specified primary contrast was episode MAE for `LEARNED_GATED − LEARNED_NO_GATE`, averaged equally across six environment cells and ten training seeds. Negative values favor gating.

- Mean paired difference: `+0.02894` MAE.
- Corrected 95% crossed hierarchical bootstrap interval: `[+0.02605, +0.03188]`.
- Interpretation: `GATED_HIGHER_ERROR`.
- The corrected interval is above zero: in this simulator and held-out hazard grid, the parameter-matched learned gated controller had higher (worse) mean target error than the learned no-gate controller.

## Descriptive cell results

| Hazard | Noise profile | Gated − no-gate MAE | Corrected 95% crossed interval |
|---:|---|---:|---:|
| 0.005 | HIGH_REVERSAL_NOISE | +0.00769 | [+0.00103, +0.01475] |
| 0.005 | EQUAL_NOISE | +0.02685 | [+0.02034, +0.03383] |
| 0.005 | REVERSED_NOISE | +0.04156 | [+0.03536, +0.04827] |
| 0.040 | HIGH_REVERSAL_NOISE | +0.02644 | [+0.01958, +0.03348] |
| 0.040 | EQUAL_NOISE | +0.03364 | [+0.02634, +0.04138] |
| 0.040 | REVERSED_NOISE | +0.03749 | [+0.03106, +0.04406] |

## Scope and limitations

- Both learned policies have exactly two trainable scalar parameters and used matched training sizes, seeds, DAgger rounds, and optimizer settings.
- The crossed bootstrap resamples ten training seeds and shared test-episode identities separately. The same episode resample is applied to all selected seeds within each cell.
- Test hazards (`0.005`, `0.04`) were not used as fixed training conditions. The three sensory-noise profile values were already present in prior M2 experiments, so only the hazard values are new holdouts.
- The privileged teacher is an oracle reference. The result does not compare against GRU/RNN families, establish generalization to other task generators, or validate the synthetic state/noise relationship as biology.
- This analysis was informed by prior M2 outcomes and remains exploratory.

## Provenance

The contract and implementation hashes are in `M2_PARAMETER_MATCHED_HAZARD_GENERALIZATION_PREFLIGHT.json`. The 90,000 episode rows and training manifest are `episode_metrics.csv` and `run_manifest.json`. `primary_result.json` preserves the original run-time summary; its initial interval is superseded by `BOOTSTRAP_CORRECTION.json`.
