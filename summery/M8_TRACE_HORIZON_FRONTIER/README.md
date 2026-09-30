# M8 — bounded credit-history frontier

**Experiment code:** `M8_TRACE_HORIZON_FRONTIER`  
**Evidence status:** post-result exploratory, outcome-informed after one implementation correction  
**Result:** horizon-64 minus horizon-1 mean accuracy `+0.1875` (95% paired task-seed bootstrap interval `[+0.1793,+0.1954]`, 30/30 seed averages positive). Exact replay remains better (mean accuracy `0.7549` versus `0.5295` for horizon 64). At delay 4, horizon 16 outperformed horizon 64.

The experiment maps a narrow synthetic performance/history-size frontier. It does not show general AI improvement, biological transfer, superiority to replay, or an NMI-level contribution. Matrix-multiplication warnings remain unresolved despite finite-value verification. See `RESULTS.md`, `EXPERIMENT_CONTRACT.md`, `IMPLEMENTATION_CORRECTION.md`, `FAILURE_LOG.md`, and `STRENGTHS.md`.
