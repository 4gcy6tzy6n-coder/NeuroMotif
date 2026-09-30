# M2_PARAMETER_MATCHED_HAZARD_V1

- Primary runner: `model/M2_PARAMETER_MATCHED_HAZARD_V1/run_parameter_matched_hazard_generalization.py`
- Post-run crossed-bootstrap correction: `model/M2_PARAMETER_MATCHED_HAZARD_V1/correct_parameter_matched_hazard_bootstrap.py`
- Schema/result summarizer: `model/M2_PARAMETER_MATCHED_HAZARD_V1/summarize_parameter_matched_hazard_generalization.py`
- Archived outputs, including initial and corrected summaries: `data/results/M2_PARAMETER_MATCHED_HAZARD_V1/`
- Frozen outcome-informed contract and preflight: this folder.

To reproduce without overwriting the archive, choose a fresh output directory and use it for all three sequential commands from the repository root:

```sh
export M2_OUTPUT_DIR="data/results/M2_PARAMETER_MATCHED_HAZARD_V1/rerun_YYYYMMDD"
python3 model/M2_PARAMETER_MATCHED_HAZARD_V1/run_parameter_matched_hazard_generalization.py
python3 model/M2_PARAMETER_MATCHED_HAZARD_V1/correct_parameter_matched_hazard_bootstrap.py
python3 model/M2_PARAMETER_MATCHED_HAZARD_V1/summarize_parameter_matched_hazard_generalization.py
```

The archived result is post-result exploratory, not biological validation. Test episodes were shared across training seeds. The original episode-level bootstrap failed to preserve that crossed identity; the corrected interval is authoritative. Original frozen-source hashes are preserved in the preflight; public copies change only repository/output routing and add the `M2_OUTPUT_DIR` override.
