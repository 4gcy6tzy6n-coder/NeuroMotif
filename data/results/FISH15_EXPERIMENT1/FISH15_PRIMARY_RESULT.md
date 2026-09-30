# Fish1.5 Experiment 1 primary result

**Decision:** `INDETERMINATE / INVALID FROZEN TOPOLOGY NULL`.

**Status:** `RETROSPECTIVE_SINGLE_SPECIMEN_DISCOVERY_WITH_PRIOR_OUTCOME_EXPOSURE`; this is not confirmatory or population-level evidence.

- Cohort: 82; defined endpoints: 82; missing endpoints: 0; single-direction endpoints: 0.
- Spearman rho: -0.1096; positive label-permutation p: 0.83372; paired neuron bootstrap 95% percentile interval: [-0.2932, 0.1338] (9844/10000 resamples had defined rho).
- The primary positive-association test does not support H1 under its frozen criterion. The overall combined decision remains indeterminate because the frozen topology-null statistic is undefined for most generated graphs.
- Topology null: 1000 unique degree-preserving/global-weight-matched rewires; defined null correlations: 139; undefined: 861; p: not estimable; frozen null yielded undefined statistics.
- The frozen graph null preserves binary in/out degrees and the global weight multiset but not each node’s weighted strengths. It is not described as strength-preserving.
- Because the frozen null produced undefined correlation statistics for at least one graph, the null test is classified invalid and no p-value is reported for it. No alternative null or endpoint was substituted.

## Structural audit

- Primary induced graph: 82 nodes, 31 ordered non-self pairs, 38 retained synapse-count annotations.
- Expanded induced graph: 97 nodes, 88 ordered non-self pairs, 111 retained annotations.
- Size values were not used. Owner presynaptic files define direction; unresolved external partners are excluded from each induced cohort.

## Secondary and fixed robustness

The frozen secondary descriptor family is in `FISH15_SECONDARY_ASSOCIATIONS.csv` with Holm adjustment. Fixed robustness outputs are in `FISH15_ROBUSTNESS_RESULTS.csv`; none replaces the primary result.
Sine phase lag and calibrated gain are not identifiable from the released data schema.

## Interpretation

All inference is conditional on one Fish1.5 specimen. Neurons, trials, frames, bootstrap samples, and null graphs are not independent animals. No causal, population-level, cross-species replication, E3, or AI-transfer claim follows.
A prior out-of-scope calculation attempt is disclosed in `../fish15/FISH15_C2_ANALYSIS_SCOPE_INCIDENT.md`; this reported analysis therefore remains retrospective and partially informed.
The secondary AUC implementation was corrected to use the frozen half-open `[60,70)` interval; see `FISH15_ANALYSIS_CORRECTION_LOG.md`.

Reproduction inputs, software versions, and hashes are recorded in `FISH15_EXPERIMENT1_PROVENANCE.json`.

## Secondary-family reporting note (2026-10-01)

The pre-specified secondary family contains five estimable graph descriptors and one constant, non-estimable three-step return descriptor. All five finite tests remain Holm-adjusted p=1.0; the constant descriptor is now explicitly reported as not estimable rather than as a p=1 test. This correction does not change the primary or combined decision. See `FISH15_SECONDARY_ASSOCIATIONS_CORRECTION.md` and `FISH15_SECONDARY_ASSOCIATIONS_CORRECTED.csv`.
