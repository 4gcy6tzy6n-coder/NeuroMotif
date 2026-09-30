# Fish1.5 Experiment 1 analysis correction log

## 2026-09-30 — AUC window boundary

- **Issue:** the initial runner integrated `POST_OFFSET_AUC_60_70` through the sample at exactly 70 seconds, although the frozen metric defines the half-open interval `[60,70)`.
- **Correction:** changed the trapezoidal integration samples to indices `[120,140)`, corresponding to the released code-defined 0.5-second timebase over `[60,69.5]`.
- **Scope:** this changes only the secondary AUC robustness value. Primary persistence, structural graph, primary correlation, permutation test, bootstrap, and topology null are unchanged by code path.
- **Disclosure:** the analysis is already retrospective and partially informed because of the prior outcome exposure described in `../fish15/FISH15_C2_ANALYSIS_SCOPE_INCIDENT.md`; this correction does not restore confirmatory status.
- **Verification:** reran `scripts/run_fish15_experiment1.py`; verify output hashes, fixed row counts, null topology uniqueness and graph invariants in the execution provenance and validation log.

## 2026-10-01 — Non-estimable secondary predictor reporting

- **Issue:** `three_step_return_strength` is constant at zero across all 82 primary neurons. The existing secondary table correctly had undefined rho/raw p, but the Holm loop emitted `1.0` as its adjusted value, which could be read as an estimable test.
- **Correction:** preserve the original table, add `FISH15_SECONDARY_ASSOCIATIONS_CORRECTED.csv`, and mark this family member `NOT_ESTIMABLE_CONSTANT_PREDICTOR` with adjusted p `NA`. The frozen family size remains six; a conservative p=1 placeholder is used only when adjusting the five finite p-values. All five estimable Holm-adjusted values remain 1.0.
- **Scope:** no new predictor, endpoint, cohort, primary statistic, permutation, bootstrap, topology null, or robustness analysis. The correction reads only the existing frozen 82-node metric table.
- **Consequence:** five estimable secondary correlations range from -0.1124 to -0.0698; none provides a positive substitute signal. Three-step recurrence cannot be tested in this sparse graph.
- **Reproduction:** `scripts/verify_fish15_secondary_associations.py`; see `FISH15_SECONDARY_ASSOCIATIONS_CORRECTION.md`.
