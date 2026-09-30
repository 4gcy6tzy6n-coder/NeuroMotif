# M8 — Truncated eligibility memory horizon frontier

**Classification:** post-result exploratory re-execution after an implementation correction; outcome-informed. This is a synthetic classification result, not biological validation or general AI transfer.

The corrected run completed 1,350 task-seed × correlation × delay × arm rows (30 seeds, 3 correlation settings, 3 delays, and five arms). All saved accuracy values were finite. The primary paired task-seed contrast, accuracy for `HORIZON_64` minus `HORIZON_1`, averaged equally over the nine correlation × delay cells, was `+0.1875` accuracy (95% paired seed-bootstrap interval `[+0.1793,+0.1954]`); all 30 seed-level averages were positive.

Mean accuracy across the nine correlation × delay settings was 0.3420 for horizon 1, 0.3796 for horizon 4, 0.4756 for horizon 16, 0.5295 for horizon 64, and 0.7549 for exact replay. The horizon effect depended on delay: at delay 4, horizon 16 reached 0.7012 and exceeded horizon 64 (0.6415); at delays 16 and 64, horizon 64 scored 0.6197 and 0.3275 respectively, above the shorter horizons. Exact replay remained the best arm across the full grid.

The computational tradeoff is substantial. A stored horizon uses `H × 64` float values (horizon 4: 256; 16: 1,024; 64: 4,096). Exact replay retains up to `D × 64` feature values (up to 4,096 at delay 64), plus the common delayed-prediction history. Therefore this experiment maps an accuracy/history-size frontier; it does not show a trace advantage over exact replay or a memory-efficiency advantage over all algorithms.

## Audit and limitations

The first execution improperly accessed the full preloaded training-feature array while computing horizon windows. It is preserved at `results_v0_invalid_unbounded_history/` and excluded. The corrected runner uses per-horizon rolling feature buffers capped at H. Since initial outcomes were inspected before this correction, the corrected run is explicitly outcome-informed and must not be described as a pristine preregistered test.

The corrected run emitted NumPy/Accelerate divide-by-zero, overflow, and invalid-operation warnings at matrix multiplication sites, despite all saved accuracies and model weights passing finite-value checks. This warning source is unresolved and remains a reproducibility limitation. The experiment uses one synthetic random-feature teacher family, fixed learning rate and discount, and post-result task choices; it does not test other objectives, trained recurrent architectures, biological transfer, or population generalization.

Reproduce with `python model/M8_TRACE_HORIZON_FRONTIER/run_experiment.py`; audit saved rows using `python model/M8_TRACE_HORIZON_FRONTIER/verify_results.py`.
