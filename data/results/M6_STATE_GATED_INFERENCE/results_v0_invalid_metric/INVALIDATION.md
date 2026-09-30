# Invalidated M6 pilot output

This run is retained for provenance only. The learned-filter metric accumulated `abs(estimate)` rather than `abs(estimate - target)`. Its learned-filter comparisons are invalid and must not be cited. The oracle HMM and no-memory rows were computed against the latent target, but the output set as a whole is superseded by `results_v2_corrected_metric/`.
