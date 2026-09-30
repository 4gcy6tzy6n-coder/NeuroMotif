# M2 targeted gain-optimization results

**Classification:** post-result, outcome-informed engineering exploration. The contract and script were frozen before this run; the optimization target was chosen after earlier negative M2 outcomes. This is not confirmatory evidence, biological validation, or biological-to-AI transfer.

## Frozen primary comparison

Ten training seeds produced two learned scalar controllers with three trainable parameters each. Both were trained directly on mean episode target-position MAE. Evaluation used 500 common-random-number episodes per seed at hazards `0.005` and `0.04` under the high-reversal-noise profile (`sigma_F=0.2`, `sigma_R=1.2`). The primary contrast was `LEARNED_MODE_GAIN − LEARNED_GENERIC_CONTEXT`; negative values favor mode-specific gain.

| Quantity | Result |
|---|---:|
| Mean paired MAE difference | `+0.000526` |
| Crossed hierarchical 95% bootstrap interval | `[-0.000395, +0.001445]` |
| Hazard `0.005` mean contrast | `-0.003637` |
| Hazard `0.04` mean contrast | `+0.004689` |
| Decision | `INCONCLUSIVE_INTERVAL_INCLUDES_ZERO` |

The primary interval crosses zero, and the two hazard-specific contrasts have opposite signs. The evidence does not show a consistent advantage for either learned controller over this two-hazard primary grid.

## Post-result diagnosis

The targeted hypothesis was that mode-specific gain might help when reversal mode reliably indicates higher observation noise. Direct optimization did learn distinct gains (across ten seeds, forward gain was about `4.16–4.19`, reversal gain about `1.26–1.29`), so the optimizer did not simply collapse the gate. Yet that learned distinction did not yield a stable advantage over the parameter-matched additive-context controller across the two hazard values. The context controller's learned additive mode bias stayed close to zero (about `−0.008` to `+0.005`), suggesting that its useful behavior came mainly from shared sensory gain and action feedback in this objective.

The remaining pattern is task-dependent: the mode-gain controller had lower MAE at hazard `0.005` and higher MAE at hazard `0.04`. The contract does not license attributing this reversal to switching frequency, controller adaptation, or another mechanism; this run did not isolate those explanations. Equal-noise and reversed-noise stress profiles also showed positive descriptive contrasts at both hazards (`+0.0091` to `+0.0199`), but these secondary conditions do not change the frozen primary decision.

## Integrity checks

- The pre-run hashes for the contract and script match the executed inputs.
- `episode_metrics.csv` contains 120,000 rows: 30,000 seed × hazard × noise-profile × episode keys, each with all four policies.
- Independent recomputation from the episode table reproduced the primary estimate and crossed interval exactly.
- The episode table SHA-256 is `3e50334e461099569f2d667212af4477f21d91fe316121835e8b24bb27d32f4`.
- Schema, paired-key completeness, and primary estimate/interval verification are in [`POSTRUN_VERIFICATION.json`](POSTRUN_VERIFICATION.json); frozen input hashes and software versions are in [`../M2_TARGETED_GAIN_OPTIMIZATION_PREFLIGHT.json`](../M2_TARGETED_GAIN_OPTIMIZATION_PREFLIGHT.json).

## Disposition

Stop this optimization line here, as specified in the contract. Do not tune further from these outcomes. The result is **inconclusive for the learned mode-specific gain versus additive-context comparison**, not evidence that state-dependent gain is universally ineffective and not a failure of the biological AFD–AIY/RIM mechanism. This work remains a simulator-specific engineering exploration and does not establish AI transfer.
