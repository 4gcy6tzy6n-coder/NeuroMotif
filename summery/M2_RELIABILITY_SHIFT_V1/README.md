# M2_RELIABILITY_SHIFT_V1

- Runner: `model/M2_RELIABILITY_SHIFT_V1/run_reliability_shift.py`
- Required helper: `model/M2_RELIABILITY_SHIFT_V1/run_state_gated_experiment.py`
- Archived sensitivity data: `data/results/M2_RELIABILITY_SHIFT_V1/`
- Primary fitted parameters are loaded from `data/results/M2_STATE_GATED_GAIN_V1/run_manifest.json`.
- Re-run from repository root with `python3 model/M2_RELIABILITY_SHIFT_V1/run_reliability_shift.py`.
- This post-result sensitivity reuses fixed parameters without retuning. Its archived outputs are copied byte-for-byte.
- In the public runner, the source-manifest lookup is redirected to the archived state-gated package, and rerun outputs go to a timestamped directory. The original machine-specific `parameter_source` path was normalized to the equivalent repository-relative path; see `PROVENANCE_NORMALIZATION.md`.
- Synthetic only; no biological data analyzed.
