# M2 on-policy DAgger follow-up

## Result

This post-result follow-up repaired the most obvious weakness in the first GRU comparator. The original GRU was trained on expert trajectories and evaluated using its own outputs, causing a likely teacher-forcing distribution shift. DAgger added on-policy states labeled by the same privileged proportional teacher and fine-tuned over three rounds.

The archived report states that the 1,025-parameter DAgger-GRU had lower mean absolute target error than the fixed gated controller in all nine cells. In the hazard 0.02 / high-reversal-noise cell, mean error was 1.502 for DAgger-GRU versus 1.556 for the gate; the paired gate-minus-GRU difference was +0.054 (95% episode-bootstrap interval [+0.0463,+0.0615]). The GRU also beat simple scalar controllers in that cell, while the privileged teacher remained better.

## Interpretation and limits

This result removes a basis for treating the original weakly trained GRU's disadvantage as evidence for the biological abstraction. It does not establish a fair capacity-matched comparison: the GRU has 1,025 parameters versus two principal fixed scalar coefficients. It is a negative result for the current fixed artificial gate in these tested closed-loop tasks, not a falsification of the biological findings.

Most importantly, the DAgger evaluation reused the same test episodes and environments already inspected for the preceding closed-loop experiment. This is a post-result repair, not independent generalization or replication. The task and mode-dependent noise remain synthetic and do not directly instantiate the biological circuit.

## Reproducibility

Episode data, summaries and manifest are copied unchanged from the archived source. Both the DAgger runner and its simulator helper are included; only output paths are redirected to timestamped package-local directories. No rerun was performed while publishing.
