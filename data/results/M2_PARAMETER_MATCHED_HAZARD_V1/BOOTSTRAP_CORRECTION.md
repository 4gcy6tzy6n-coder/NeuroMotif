# Post-run bootstrap correction

**Status:** `REPORTING_CORRECTION`; controller training and simulation outputs are unchanged.

The initial hierarchical bootstrap sampled test episode indices independently for each fitted controller seed. In the actual design, the same 300 exogenous episodes in each environment cell were reused across all ten training seeds. Independent resampling therefore failed to preserve the crossed dependence induced by common random numbers and could understate uncertainty.

The paired point estimate is unchanged at `+0.02894` MAE. The initially reported interval was `[0.027708945683354053, 0.03021035148407733]`; it is superseded by the crossed-factor interval `[ +0.02605, +0.03188 ]`.

The corrected bootstrap resamples training seeds and, separately, shared test-episode identities within each environment cell. The same sampled episode identities are applied to every selected training seed. Cell-specific intervals use the analogous crossed resampling for that cell.

Corrected frozen interpretation: `GATED_HIGHER_ERROR`.

| Hazard | Noise profile | Mean gated − no-gate MAE | Corrected crossed 95% interval |
|---:|---|---:|---:|
| 0.005 | HIGH_REVERSAL_NOISE | +0.00769 | [+0.00103, +0.01475] |
| 0.005 | EQUAL_NOISE | +0.02685 | [+0.02034, +0.03383] |
| 0.005 | REVERSED_NOISE | +0.04156 | [+0.03536, +0.04827] |
| 0.040 | HIGH_REVERSAL_NOISE | +0.02644 | [+0.01958, +0.03348] |
| 0.040 | EQUAL_NOISE | +0.03364 | [+0.02634, +0.04138] |
| 0.040 | REVERSED_NOISE | +0.03749 | [+0.03106, +0.04406] |

This is a transparent post-run correction to uncertainty estimation, not a change to the contrast, outcome, task, model, or episode data. The original run output remains preserved in `primary_result.json`; `BOOTSTRAP_CORRECTION.json` is authoritative for corrected intervals.
