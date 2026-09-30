# M8 memory matched replay analysis

Re-run from the repository root with `python model/M8_MEMORY_MATCHED_REPLAY_ANALYSIS/analyze.py`. It reads the archived M8 task metrics at `data/results/M8_TRACE_HORIZON_FRONTIER/task_metrics.csv` and writes a fresh output directory under `data/results/M8_MEMORY_MATCHED_REPLAY_ANALYSIS/reproductions/`. The local detailed-record runner writes to its own `experiments/.../results` folder. This is a post-result analysis reusing M8 task outcomes, not an independent experiment; see `summery/M8_MEMORY_MATCHED_REPLAY_ANALYSIS/` for interpretation and limits.
