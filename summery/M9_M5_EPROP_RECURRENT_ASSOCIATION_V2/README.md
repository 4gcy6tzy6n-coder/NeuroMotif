# M9-v2 — training-exposure optimization

M9-v1's 500 episodes left long-delay test accuracy near four-class chance. This separate, post-result version changed only training exposure to 3,000 episodes and used disjoint task seeds 200–229.

The BPTT viability criterion passed at all delays: mean accuracy was 0.7116 (D4), 0.5079 (D16), and 0.2873 (D64); each seed-bootstrap 95% lower bound exceeded chance 0.25. Eligibility trace beat the one-step no-trace update by 0.0906 accuracy overall (95% CI [0.0828, 0.0988], 30/30 seeds), but remained below BPTT by 0.0114 (95% CI [−0.0193, −0.0037]). At D64 alone the trace-minus-no-trace interval crossed zero.

Interpretation is limited to this synthetic task and trainable leaky RNN. It is not an LTC/LNN, general task-family transfer, or biological validation. The initial runner completed the numerical calculation but failed when it looked for the wrong contract filename during manifest writing; all 270 metric cells and summaries were independently checked from the saved table, and the defect and recovery are retained.
