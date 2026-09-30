# M2 parameter-matched hazard generalization

## Result

Ten independent training seeds fit a pair of two-parameter scalar controllers using matched data and DAgger settings. They were tested on six cells formed by two hazard values and three noise profiles, with 300 episodes per cell. The single primary contrast was mean absolute error for learned gated minus learned no-gate, averaged equally across cells and training seeds; positive values mean the gated controller has worse error.

The archived primary result is +0.02894 MAE. The original episode bootstrap was corrected because test-episode identities were shared across training seeds. The crossed hierarchical 95% interval is [+0.02605, +0.03188], above zero. All six descriptive cell contrasts are positive, with corrected intervals above zero. The corrected interval, not the superseded initial interval, is the reportable result.

## Interpretation and limits

In this synthetic simulator, the parameter-matched learned gated controller had higher error than the learned no-gate controller on the declared test grid. This is unfavorable to the tested artificial gate. It is not a biological failure result. The task/noise relationship remains synthetic, the study was outcome-informed by prior M2 results, and it does not test generic GRU/RNN families or other task generators.

The two hazard values were not used as fixed training conditions, but the noise profiles were already used in prior M2 rounds; describe these hazards as held-out values within the same task family, not as a fully independent task family. The privileged teacher is an oracle, not a fair learned comparator.

## Bootstrap correction and reproducibility

The original episode bootstrap independently resampled episode indices within training seeds even though the same exogenous test streams were shared. The corrected method resamples training seeds and shared episode IDs as crossed factors; the point estimate is unchanged. Both original and corrected artifacts are retained, with the initial interval explicitly superseded.

The 90,000-row episode file, training manifest, initial result, corrected result, correction record, schema check, contract, and preflight are preserved. Public scripts retain the source computation; their paths are redirected to the repository and they support a common `M2_OUTPUT_DIR` so a rerun, correction, and summary can share one fresh folder without modifying the archive. No experiment was rerun while publishing.
