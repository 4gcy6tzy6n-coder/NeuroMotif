# M2_RELIABILITY_SHIFT_V0_ARCHIVE provenance path normalization

The archived `run_manifest.json` originally stored a machine-specific absolute path for the parameter source. It has been replaced with the repository-relative path `data/results/M2_STATE_GATED_GAIN_V1/run_manifest.json`. The referenced manifest is byte-identical to the source manifest used by the original analysis (SHA-256 `e7cfca441350c0b3f6fd26a6617845eb4f7140d9a3931018a7a70a533613e6c5`). Semantic JSON comparison confirms that only `parameter_source` changed; outcome values and all other metadata are unchanged.
