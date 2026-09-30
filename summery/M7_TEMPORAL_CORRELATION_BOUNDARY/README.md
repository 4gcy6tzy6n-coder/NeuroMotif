# M7 — Temporal-correlation boundary for eligibility traces

**Status:** Completed post-result exploratory synthetic sweep; not biological validation or an algorithm-novelty claim.

## Question and result

How does input autocorrelation interact with the benefit of a fixed eligibility trace across delay and objective? In this random-feature teacher family, trace benefit relative to a current-input update varies with correlation and delay, with reversals at some cells. Exact replay outperformed eligibility in all 48 objective × correlation × delay cells.

## Strengths

- Keeps 30 paired task seeds and reports classification and regression separately.
- Retains exact replay as a strong reference and preserves raw task metrics.
- Makes the limited comparator claim explicit: boundary conditions against current-input updates, not superiority to exact memory or offline learning.

## Failure lessons

- The original pooled interaction mixed classification accuracy points and regression MSE points. Its pooled value is invalid and excluded; use `archive/analysis_v1_objective_stratified.json` as the authoritative analysis.
- The eligibility trace never beats exact replay in the 48 tested cells. This does not establish a general performance–memory tradeoff because replay budget, truncated replay, BPTT, and trained recurrent networks were not compared.
- The study is post-result and remains within one synthetic task family; it cannot validate a biological trace parameter or general AI benefit.

## Package map

- `../../model/M7_TEMPORAL_CORRELATION_BOUNDARY/`: contract, runner, and unit-safe analyzer.
- `../../data/results/M7_TEMPORAL_CORRELATION_BOUNDARY/archive/`: raw outcomes, original summaries, and authoritative corrected analysis.
- This directory: result interpretation and correction history.

The public runner and analyzer were adapted only to use fresh timestamped output paths (or documented environment variables); neither was executed during publication. Archived outcome and analysis files are copied from the source record without recomputation.
