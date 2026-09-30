# Fish1.5 post-result recurrence-conditioned null v1

**Status:** exploratory, outcome-informed sensitivity analysis. This does not replace or amend the frozen Experiment 1 primary result.

## Why this follow-up was run

The original 82-node primary graph contains 31 directed weighted edges and 38 retained annotation records. Its frozen local-recurrence index is zero for 78/82 neurons; only two reciprocal dyads (four neurons) have nonzero recurrence. The original unconstrained degree-preserving null destroys all reciprocal dyads in most sampled graphs, leaving a constant predictor and producing 861/1,000 undefined Spearman correlations. That original null comparison remains invalid.

## Conditional null result

The post-result follow-up generated 1,000 unique directed graphs by same-weight double-edge swaps, conditioning on exactly two reciprocal dyads. It preserved the node set, 31-edge count, binary in/out degree sequence, every node's weighted in/out strengths, and the global edge-weight multiset. All saved statistic rows are finite and all reported invariant flags equal one.

The observed Spearman association was `rho = -0.10962`. The conditional-null rho mean was `-0.01964` (2.5–97.5% quantiles `[-0.18161, +0.15678]`). The upper-tail empirical proportion was `0.9181`; the descriptive two-sided absolute-tail proportion was `0.1998`. This conditional null does not show that recurrence placement is unusually aligned with greater persistence. It also conditions on the observed amount of reciprocity, so it cannot test whether the graph has an unusual amount of recurrence.

## Sampling and verification limits

Although the run saved 1,000 distinct graph hashes, the null statistic sequence had lag-1 autocorrelation `0.714`; an initial-positive-sequence diagnostic estimated effective sample size near `150` (approximate MC standard error of the null mean `0.00689`). Mixing is therefore unresolved, and the empirical tail fractions are descriptive rather than well-calibrated confirmatory p-values. The saved package contains topology hashes and per-graph invariant flags but not edge lists, so the post-run check did not independently reconstruct every graph's invariants from edge states. The invariant checks are supported by the frozen same-weight swap implementation and its per-state flags, with that audit boundary disclosed.

## Project interpretation

The primary positive association test remains `NOT_SUPPORTED` (`rho=-0.10962`, directional permutation `p=0.8337`, bootstrap interval `[-0.2932,+0.1338]`). The original frozen topology-null test remains invalid. This follow-up adds a sparse-graph diagnostic and a constrained descriptive comparison; it does not establish a positive local-recurrence motif, a biological absence, causality, animal-level replication, or population generalization. The whole Fish1.5 Experiment 1 disposition remains retrospective and single-specimen; its combined frozen-contract decision remains `INDETERMINATE`.

## Reproduction artifacts

- Contract: `POSTRESULT_NULL_CONTRACT.md`
- Preflight hashes: `PREFLIGHT.json`
- Runner: `scripts/run_fish15_recurrence_conditioned_null.py`
- Verification code: `scripts/verify_fish15_recurrence_conditioned_null.py`
- Per-graph statistics: `CONDITIONED_NULL_RESULTS.csv`
- Summary and diagnostics: `CONDITIONED_NULL_SUMMARY.json`, `POSTRUN_VERIFICATION.json`
