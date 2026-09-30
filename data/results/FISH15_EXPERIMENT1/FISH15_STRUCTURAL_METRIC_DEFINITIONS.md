# Fish1.5 structural metric definitions — retrospective freeze

**Status:** `RETROSPECTIVELY_SPECIFIED`; this contract is set before Experiment 1 outcome computation. Structural identity/schema knowledge and the 97-ID partner audit were inspected earlier, so no claim of outcome-blind prospective design is made.

## Cohort and graph source

- Primary nodes are exactly the 82 functional IDs with `structurally_complete=YES` in `FISH15_C2_97_NEURON_STRUCTURAL_COVERAGE.csv`. The 15 other crosswalk IDs are sensitivity-only, as already specified in the user-provided task. No neuron may be removed or added using its calcium values or computed metrics.
- Source is the checksummed Zenodo v1 owner-centered archive and the explicit official functional→EM crosswalk. No fuzzy identity join is permitted.
- Directed rows are read from each focal neuron's `*_presynapses.csv`: archive focal `axon_id` → partner `postsynaptic_ID`; partner maps to a functional node only by exact match to its crosswalk `dendrite_id`.
- Use only `validation_status=valid`; the official export code defines predicted-row validity as size greater than its preset cutoff and marks manual rows valid. Include predicted and manual validated rows. Do not read, sum or use the `size` values. Exclude `below cut-off` rows. No manual/predicted duplication is silently deduplicated: use exact nonmissing `synapse_id` within the focal owner when available; manual rows without IDs use only the archive row as one annotation record, and any duplicate owner/partner/coordinate key must be logged as an unresolved identity ambiguity before graph construction.
- `W_ij` is the number of retained presynaptic annotation records from primary neuron i to primary neuron j. Repeated records are synapse-count weight; rows whose partner does not resolve to a primary node are external to the induced 82-node graph. No size/strength sum is used.
- Self-edges are excluded from recurrence descriptors. Reciprocal edge-pair counts use the directed binary support `B_ij = 1[W_ij>0]`.

## Frozen descriptors

For each primary neuron i, sums below range over primary nodes j,k distinct from i. For `in_strength_i` and `out_strength_i`, use W (synapse counts), not the unfiltered archive.

- `in_strength_i = sum_j W_ji`; `out_strength_i = sum_j W_ij`.
- `reciprocal_strength_i = sum_j min(W_ij,W_ji)`.
- `reciprocal_fraction_i = (# j with B_ij=B_ji=1) / (# j with B_ij=1 or B_ji=1)`; if denominator is zero, define 0.
- `two_step_return_strength_i = sum_j W_ij W_ji`.
- `three_step_return_strength_i = sum_{j!=k, j,k!=i} W_ij W_jk W_ki`.
- **Primary predictor `LOCAL_RECURRENCE_INDEX_i`:** `two_step_return_strength_i / (out_strength_i * in_strength_i)` when the denominator is positive; define 0 when either strength is zero. This is a weighted fraction of possible two-edge out/in combinations that form a return walk, and is defined for every primary node.

These quantities describe this induced graph. They are not synaptic efficacy, causal feedback, or a motif-enrichment result.

## Matched topology null

Generate 1,000 unique directed double-edge-swap graphs on the fixed 82 primary nodes. Exclude self-loops and duplicate ordered pairs. Each accepted swap preserves the exact binary in/out degree sequence and edge count. Reassign the observed multiset of retained synapse-count weights uniformly to the rewired edges; this preserves the global weight distribution, but **does not preserve each node's weighted in/out strength**. Do not describe this as a strength-preserving null. Use a fixed seed from a frozen config, require at least 10×E accepted swaps between saved null graphs, reject duplicate graph states, and record all invariant checks. If 1,000 valid states cannot be generated, report the null as unavailable; do not change the null family or number after seeing results.

The edge-list-to-pair reduction must first reconcile exact synapse IDs and owner-direction duplicates. If the pre- versus postsynaptic owner views disagree for a mapped directed pair, the presynaptic owner table is primary for W; discrepancies are reported in the schema audit and never repaired by adding the reverse-view-only edge.
