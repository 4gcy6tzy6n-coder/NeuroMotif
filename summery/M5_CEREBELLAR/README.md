# M5 — cerebellar delayed teaching / eligibility benchmark

**Status:** post-result exploratory synthetic study. The results do not validate a biological learning rule or constitute confirmatory AI transfer.

## Biological evidence scope

Kimpo et al. (2014, DOI: 10.7554/eLife.02076) and Silva et al. (2024, DOI: 10.1038/s41593-024-01594-7) support a task-bounded causal role for climbing-fiber teaching events in associative eyeblink learning. They do not determine the exact plasticity equation or establish a universal cerebellar rule. The source experiments also have limitations, including small group sizes and tool-specific caveats described in `RESULTS.md`.

## Positive computational result

In v3, an eligibility trace improved accuracy over a no-trace online update by a mean +0.2868 across delays 1, 4, 16, and 64; seed-cluster bootstrap 95% interval [+0.2712, +0.3010] across 30 task seeds. This is a narrow result on a synthetic stream.

## Limitations and failures

- The trace remained below exact replay and batch logistic at every delay; accuracy degraded at the longest delay.
- v1's apparent gain was partly confounded by larger update norms.
- v2 norm matching used the target feature's norm, leaking information unavailable to a strictly local learner.
- v3 corrected both issues using unit-normalized inputs and only the current local trace norm. Because these corrections followed inspection of earlier outcomes, v3 remains post-result exploratory.
- Replay and batch comparators have different memory/data access, so the comparison does not establish broad algorithmic superiority.

## Files

- Code: [`model/M5_CEREBELLAR/run_delayed_teaching.py`](../../../model/M5_CEREBELLAR/run_delayed_teaching.py)
- Results: [`data/results/M5_CEREBELLAR/`](../../../data/results/M5_CEREBELLAR/)
- Protocol versions and detailed interpretation: this directory.
