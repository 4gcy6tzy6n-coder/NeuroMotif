# Fish1.5 Experiment 1 analysis correction log

## 2026-09-30 — AUC window boundary

- **Issue:** the initial runner integrated `POST_OFFSET_AUC_60_70` through the sample at exactly 70 seconds, although the frozen metric defines the half-open interval `[60,70)`.
- **Correction:** changed the trapezoidal integration samples to indices `[120,140)`, corresponding to the released code-defined 0.5-second timebase over `[60,69.5]`.
- **Scope:** this changes only the secondary AUC robustness value. Primary persistence, structural graph, primary correlation, permutation test, bootstrap, and topology null are unchanged by code path.
- **Disclosure:** the analysis is already retrospective and partially informed because of the prior outcome exposure described in `../fish15/FISH15_C2_ANALYSIS_SCOPE_INCIDENT.md`; this correction does not restore confirmatory status.
- **Verification:** reran `scripts/run_fish15_experiment1.py`; verify output hashes, fixed row counts, null topology uniqueness and graph invariants in the execution provenance and validation log.
