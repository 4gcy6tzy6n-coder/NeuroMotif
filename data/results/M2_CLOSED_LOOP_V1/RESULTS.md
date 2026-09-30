# Experiment 3 results: closed-loop target tracking

**Status:** completed exploratory synthetic control experiment. It uses no biological outcome values. The reversal-state noise profile is a designed stress condition, not established by the *C. elegans* source study.

## Main result

In all nine combinations of target-switch rate and sensory profile, the fixed state-gated controller had higher mean absolute target error than both the occupancy-matched no-gate feedback controller and the ungated memoryless controller. It therefore did **not** improve navigation in this closed-loop task.

At target hazard `0.02` in the high-reversal-noise profile (`σ_F=0.2`, `σ_R=1.2`), gated mean absolute error was `1.5561`, versus `1.5193` for occupancy-matched no-gate feedback (paired difference `+0.0367`, 95% episode-bootstrap interval `[+0.0293,+0.0446]`; 300 episodes). The gated controller's target-zone fraction was `0.4756`, versus `0.4792` for no-gate (difference `−0.0036`, 95% interval `[−0.0064,−0.0008]`).

The effect was also negative when sensory reliability was equal (`+0.0425` position error at hazard `0.02`) and reversed (`+0.0495` at hazard `0.02`). This rejects the claim that the chosen fixed gate/feedback settings generally improve closed-loop navigation. It is consistent with action persistence causing overshoot and lag in this particular controller/task.

## Recurrent baseline status

The initial 1,025-parameter GRU's imitation loss fell from `0.2430` to `0.0149` over eight training epochs, but it underperformed fixed controllers on test mean error. It used teacher-forced previous actions at training and its own outputs at evaluation, creating a likely state-distribution mismatch. A post-result DAgger follow-up corrected that issue and the updated GRU outperformed the fixed gated controller in all nine cells; see [`../CLOSED_LOOP_DAGGER_RESULTS.md`](../CLOSED_LOOP_DAGGER_RESULTS.md). This follow-up reuses the same already-inspected test environments, so it is exploratory rather than independent confirmation.

The privileged proportional teacher, which observes true position error, had lower mean error than all observation-limited policies across the tested cells. This confirms a nonzero observation/noise limitation in the task; it does not validate the gate.

## Interpretation and boundary

This result is unfavorable to the current fixed state-gated controller. It shows that a gate that helps a one-step noisy classification task need not help a closed-loop control task, even when actions determine the next observation. The task supplies motor context directly and imposes mode-dependent measurement noise; neither feature has been established as the mechanism's full biological implementation. The result is an artificial-controller boundary, not a biological mechanism failure.

## Reproducibility

- Definition: [`CLOSED_LOOP_EXPERIMENT_CONTRACT.md`](../CLOSED_LOOP_EXPERIMENT_CONTRACT.md).
- Implementation: [`run_closed_loop_experiment.py`](../run_closed_loop_experiment.py).
- Episode-level results: `episode_metrics.csv`.
- Cell summaries and paired intervals: `condition_summary.json`.
- Seed, training, policy, and simulator details: `run_manifest.json`.
- Independent unit: episode; each episode is 240 steps.
