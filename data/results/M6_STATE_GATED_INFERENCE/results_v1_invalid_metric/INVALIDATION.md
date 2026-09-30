# Invalidated M6 output

This output is retained for provenance only. It has the same metric bug as `results_v0_invalid_metric/`: the learned-filter metric accumulated `abs(estimate)` rather than `abs(estimate - target)`. An attempted patch did not change the executed line, so this output is also invalid. Do not cite its learned-filter comparisons. It is superseded by `results_v2_corrected_metric/`.
