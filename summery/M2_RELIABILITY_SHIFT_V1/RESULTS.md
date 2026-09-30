# M2 reliability-shift sensitivity

## Design and result

This post-result sensitivity analysis kept the state-gated and additive coefficients selected in the earlier experiment fixed, without retuning. It tested equal forward/reversal observation reliability and a reversed relation in which reversal observations were cleaner. The design crosses two reliability relations, three forward-noise levels, and four hazard values, with 300 episodes per cell. Episode is the independent unit.

At hazard 0.01 and equal noise σF=σR=0.8, the archived state-gating report gives accuracy 0.9713 for the fixed gated controller, compared with 0.9782 for the additive control and 0.9785 for the occupancy-matched no-gate control. In a representative reversed-reliability condition (σF=0.8, σR=0.4), gated accuracy was 0.9720 and additive accuracy 0.9804. These examples are consistent with the conclusion that the earlier gate advantage depends on the task's mode/reliability mapping.

## Interpretation and limits

These are post-result sensitivity checks, not preregistered or confirmatory evidence. They deliberately alter a synthetic task assumption while holding the previously selected parameters fixed. They show that the synthetic gate's performance advantage does not transfer unchanged when the state-to-reliability relationship is removed or reversed.

The biological source establishes motor-state dependence in AIY activity and RIM-dependent corollary discharge; it does not establish the synthetic assumption that forward/reversal states carry different sensory-noise levels. This sensitivity analysis therefore tests robustness of the model assumption, not a biological claim. It provides no organism-level validation or general AI inductive-bias evidence.

## Reproducibility

Archived episode metrics, condition summary, and manifest are byte-identical to source. The release includes the primary experiment helper and reads its frozen selected parameters from the archived state-gated manifest. Only the public runner's manifest lookup and output routing were adapted to repository paths.
