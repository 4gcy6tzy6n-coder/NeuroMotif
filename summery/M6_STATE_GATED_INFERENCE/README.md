# M6 — State-gated inference

**Status:** Completed exploratory synthetic study; not biological validation or a confirmatory test.

## Question and result

Does a context-gated sensory gain generalize better than a parameter-count-matched innovation-adaptive filter? On the primary high-reversal-noise profile, the state-gated filter had higher mean absolute error than the innovation-adaptive filter at all three held-out switch hazards. The equal-weight mean difference (gate minus adaptive) was `+0.07587` (crossed 95% interval `[+0.07314, +0.07864]`). The gate beat a single global gain descriptively, but did not beat generic adaptation. Performance also worsened under equal and reversed context/noise mappings.

## Strengths

- Uses paired held-out trajectories and crossed resampling over training seeds and shared test episodes.
- Includes a same-parameter generic adaptive control and clearly labels the oracle as model-informed.
- Preserves the metric correction history and identifies the final corrected run as authoritative.

## Failure lessons

- The first two exploratory outputs used `abs(estimate)` rather than `abs(estimate - target)` and are invalid. They remain archived with invalidation notes; only `results_v2_corrected_metric` is authoritative.
- The direct state-gated abstraction loses to a generic residual-adaptive filter on every primary hazard cell. This is not evidence against the worm mechanism; the synthetic task assumes a context–noise relation not established biologically.
- The oracle is nearly exact on this simple generator, so the task is not by itself a broad AI benchmark.

## Package map

- `../../model/M6_STATE_GATED_INFERENCE/`: contract and executable model source.
- `../../data/results/M6_STATE_GATED_INFERENCE/`: final and superseded outputs, run manifest, and package hash manifest.
- This directory: result interpretation and correction history.

The public runner was adapted only to write to a fresh timestamped output directory (or `M6_OUTPUT_DIR`); it was not executed during publication. Archived outcome files are copied from the source record without recomputation.
