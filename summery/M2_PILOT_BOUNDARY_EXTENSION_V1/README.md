# M2_PILOT_BOUNDARY_EXTENSION_V1

- Model runners: `model/M2_PILOT_BOUNDARY_EXTENSION_V1/run_pilot.py` and `run_boundary_sweep.py`
- Archived outputs: `data/results/M2_PILOT_BOUNDARY_EXTENSION_V1/`
- Interpretation and limitations: `summery/M2_PILOT_BOUNDARY_EXTENSION_V1/RESULTS.md`
- Re-run the post-pilot extension from repository root with `python3 model/M2_PILOT_BOUNDARY_EXTENSION_V1/run_boundary_sweep.py`.
- Each rerun writes to a new timestamped folder and does not overwrite archived outputs.
- Both scripts preserve the source calculations; only output paths were redirected to this repository's package. The extension imports the pilot's simulation function.
- Exploratory synthetic results only. No biological data or biological outcomes were analyzed.
- The archive contains the original 5,400-row episode-level CSV, condition summary, and run manifest. Historical Python/NumPy versions for this extension are not recorded in its manifest.
