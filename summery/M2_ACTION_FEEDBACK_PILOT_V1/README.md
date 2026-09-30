# M2_ACTION_FEEDBACK_PILOT_V1

- Model: `model/M2_ACTION_FEEDBACK_PILOT_V1/run_pilot.py`
- Archived result: `data/results/M2_ACTION_FEEDBACK_PILOT_V1/`
- Scientific summary: `summery/M2_ACTION_FEEDBACK_PILOT_V1/RESULTS.md`
- Re-run the simulator from repository root: `python3 model/M2_ACTION_FEEDBACK_PILOT_V1/run_pilot.py`.
- Recompute paired intervals from the archived pilot and boundary-extension episodes with `python3 model/M2_ACTION_FEEDBACK_PILOT_V1/analyze_pilot.py`; the result is written to a new timestamped analysis directory. The archived `pilot_paired_contrasts.json` preserves the original analysis output.
- Each rerun writes to a new timestamped directory; it does not overwrite the archived result.
- Synthetic-only exploratory result; no biological values were analyzed.
- NumPy version in the historical manifest: 2.4.4. Python version and a dependency lock were not captured for this run.
