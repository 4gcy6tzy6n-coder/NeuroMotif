# Fish1.5 post-result recurrence-conditioned topology-null audit v1

**Status:** outcome-informed exploratory sensitivity analysis. The original Fish1.5 Experiment 1 contract, primary endpoint/predictor, observed association, and invalid frozen-null result remain unchanged. This amendment was motivated by inspecting the completed null output and its degeneracy; it is not confirmatory and cannot rescue or replace the original test.

## Diagnostic premise

The completed 82-node primary induced graph has 31 directed weighted edges, 38 retained synapse-count annotations, and only two reciprocal dyads (four nodes with nonzero local recurrence). The frozen unconstrained degree-preserving rewire usually removes all reciprocal dyads, making the recurrence predictor constant and Spearman rho undefined. The new null conditions on the observed number of reciprocal dyads so it can ask a narrower question: conditional on this unusually sparse graph's degree and strength sequence and its total reciprocal-dyad count, is the observed placement of recurrent dyads across nodes unusually aligned with the already-defined persistence endpoint?

## Fixed method

- Reconstruct the exact 82-node weighted directed graph by calling the original `scripts/run_fish15_experiment1.py` graph builder on the frozen crosswalk, cohort file, and Zenodo v1 archive. Verify the node order against the existing `primary82` rows in `FISH15_NEURON_METRICS.csv`.
- Keep the already-computed persistence endpoint fixed; do not recalculate, filter, or alter it.
- Generate 1,000 unique directed topologies with double-edge swaps. A candidate swap is accepted only when it is loop-free, has no duplicate ordered pair, and preserves the observed count of reciprocal dyads.
- Swap only two edges having the same synapse-count weight. This preserves exactly: node set, edge count, binary in/out degree sequence, each node's weighted in/out strength, and the global weight multiset. It also preserves the total number of reciprocal dyads (two), while changing their node placement and the remaining edge arrangement.
- Require at least `10 × 31 = 310` accepted swaps between saved states. Cap the chain at 50,000,000 proposals. Reject repeated binary topologies. If 1,000 unique valid graphs are not obtained, report the conditional null unavailable; do not loosen constraints.
- For each graph, compute the original `LOCAL_RECURRENCE_INDEX` formula and its Spearman correlation with fixed persistence across the same 82 neurons. All 1,000 statistics must be finite; otherwise the conditional null itself is invalid.
- Primary null comparison is upper-tail `(1 + count(null_rho >= observed_rho))/1001`, matching the original positive-direction topology-null tail. Also report a two-sided absolute-tail empirical fraction descriptively. Neither comparison changes the original directional primary permutation test.

## Interpretation boundary

This is a post-result, single-specimen conditional graph sensitivity check. It conditions on the observed total reciprocity and node-level weighted strengths, so it does not test whether the specimen has more reciprocity than a generic graph. It tests only whether the specific placement of recurrence among this graph's neurons is unusually associated with the previously measured persistence values under this constrained randomization. The null family and conditional question were selected after the original outcome and null degeneracy were known. Do not call the new p-value confirmatory, animal-level, causal, or a validated motif result. The primary association remains `NOT_SUPPORTED`; the historical frozen-null comparison remains invalid.

## Stop rule

Run this null generation once. Preserve all failures. Do not tune constraints, swap counts, or endpoints after inspecting the output. Stop after the independent invariant and statistic verification is written.
