# M2 closed-loop target tracking

## Result

The synthetic 1-D closed-loop task compared a fixed motor-state-gated feedback controller with occupancy-matched no-gate feedback, sensory-only controls, an imitation-trained GRU, and a privileged teacher. It used 300 test episodes per cell across three target-switch hazards and three sensory-noise profiles; one episode is the independent unit.

The archived result reports that gated feedback had higher mean absolute target error than both occupancy-matched no-gate feedback and the ungated memoryless controller in all nine cells. At hazard 0.02 in the high-reversal-noise profile, mean absolute error was 1.5561 for gated feedback and 1.5193 for no-gate feedback; target-zone fraction was 0.4756 versus 0.4792. The privileged teacher, which observes true state, performed better than observation-limited policies.

## Interpretation and limits

This result is unfavorable to the selected fixed state-gated controller in this closed-loop task. A gate that improved some one-step synthetic classification settings did not improve closed-loop navigation; the result is consistent with action persistence causing overshoot or lag for this controller. This is an artificial-task boundary, not a biological mechanism failure.

The task directly supplies motor context and imposes synthetic mode-dependent noise. Neither implements the full biological pathway. The GRU had 1,025 parameters and was trained by teacher forcing, then evaluated using its own outputs; the source report identifies this as a likely state-distribution mismatch. A post-result DAgger follow-up reused these test environments, so it is not independent confirmation and is archived separately.

## Reproducibility

The episode CSV, condition summary, manifest, result note, and contract are preserved with the package. The public runner changes only output routing; no rerun was performed while publishing. The original manifest does not record historical package versions or a dependency lock.
