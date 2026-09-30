# FISH15_EXPERIMENT1 — Fish1.5 specimen-level structure–dynamics analysis

**Classification:** retrospective, partially outcome-informed, single specimen; not confirmatory and not population-level.

## Result

The frozen primary analysis used 82 structurally complete neuron identities and the predefined local recurrence index / post-offset persistence pair. Spearman rho was **−0.1096**, the one-sided positive-label permutation p-value was **0.83372**, and the within-specimen neuron bootstrap 95% interval was **[−0.2932, 0.1338]**. The positive H1 was **not supported**.

The prespecified topology null produced 1,000 unique binary degree-preserving, global-weight-matched rewires, but only **139/1,000** had a defined correlation. Its inferential test is therefore **invalid / indeterminate**; no null p-value is reported. The combined experiment decision remains `INDETERMINATE / INVALID FROZEN TOPOLOGY NULL`.

## Strengths

- Uses an explicit same-specimen functional-to-EM identity crosswalk and presynaptic owner tables for edge direction.
- Keeps the primary cohort, endpoint, predictor, test, and null family explicit; reports both the unsupported primary direction and the null-model failure.
- Preserves the single-specimen scope and distinguishes neurons, trials, frames, and null graphs from independent animals.
- Does not use missing synapse-size values, infer L/R identity, claim causal edge transmission, or generalize to a zebrafish population.
- A clean rerun on the recorded runtime reproduced the reported primary statistics and graph coverage counts.

## Failure experience and limitations

- The primary association is small and negative, with an interval spanning zero; this specimen does not support the stated positive association.
- The induced 82-neuron graph is sparse (31 directed non-self pairs; 38 retained annotations), and local recurrence is too degenerate under the frozen null: most rewires yield constant recurrence values and undefined correlations.
- The null does not preserve node-level weighted strengths. That limitation was stated in advance and is not repaired by this result package.
- The analysis is retrospective and partially outcome-informed, uses one specimen, and cannot establish animal-population effects or causality.
- This round does not clear E3, establish cross-species convergence, or test AI transfer. A later constrained-null sensitivity analysis is a separate follow-up round and is not substituted here.

## Files

- `data/results/FISH15_EXPERIMENT1/` — metrics, frozen null output, provenance, and figure source/output artifacts.
- `model/FISH15_EXPERIMENT1/` — reproducible analysis runner and input instructions.
- This directory — standalone contract, definitions, result interpretation, correction log, and validation record.

A limited 2026-10-01 reporting correction marks the constant three-step return predictor as not estimable. It does not change the primary or combined decision. See `FISH15_SECONDARY_ASSOCIATIONS_CORRECTION.md`.
