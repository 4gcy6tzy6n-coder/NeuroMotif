# M2_PILOT_BAYESIAN_BENCHMARK_V1

- Model runners: `model/M2_PILOT_BAYESIAN_BENCHMARK_V1/run_pilot.py` and `run_bayesian_benchmark.py`
- Archived outputs: `data/results/M2_PILOT_BAYESIAN_BENCHMARK_V1/`
- Results and limitations: `summery/M2_PILOT_BAYESIAN_BENCHMARK_V1/RESULTS.md`
- Re-run from repository root with `python3 model/M2_PILOT_BAYESIAN_BENCHMARK_V1/run_bayesian_benchmark.py`.
- Each rerun writes to a timestamped output folder; it does not overwrite the archived run.
- The release runners preserve the source calculations and redirect output paths only. The Bayesian benchmark imports the pilot constants.
- Synthetic-only computational experiment; no biological data or biological outcomes were analyzed.
- The oracle is task-specific and knows the target-switch hazard, sensor noise, and artifact transition. It is an upper-bound reference, not a capacity-matched learned baseline.
- Historical Python/NumPy versions are not recorded in this run manifest.
