# M10_M5_EPROP_TEMPORAL_XOR_V1 — summary and failure experience

**Status:** `INCONCLUSIVE_TASK_NOT_LEARNABLE_ACROSS_GRID`
**Classification:** post-result exploratory synthetic recurrent-network benchmark. The benchmark tests a delayed two-cue XOR task in an artificial 24-unit leaky tanh RNN. It is not biological validation, an LNN/LTC experiment, connectome transfer, or general AI evidence.

## Frozen question and decision rule

Compare eligibility-trace learning with no-trace local learning, using task seed as the independent unit and equally averaging over delays 4, 16, and 64. Before interpreting that contrast, the exact-BPTT reference had to pass the task-viability gate: the lower 95% seed-bootstrap bound must exceed binary chance (0.50) at every delay.

## Result

The primary eligibility-minus-no-trace contrast was -0.00033 accuracy (95% task-seed bootstrap CI [-0.00209, +0.00167]); 8/30 seeds favored eligibility. Mean held-out accuracies were 0.50091 for eligibility, 0.50124 for no-trace, and 0.50089 for BPTT. BPTT's lower bounds were 0.49793, 0.49287, and 0.48787 at delays 4, 16, and 64. The viability gate failed at every delay.

## Analysis and failure experience

All arms were near binary chance. The learning-rule contrast therefore cannot answer whether eligibility helps on a learnable version of this task. It is not evidence that eligibility is ineffective. The failure shows that task viability must be demonstrated before interpreting the learning-rule comparison. The finite-difference check and independent integrity audit passed, but they establish implementation/data integrity rather than task learnability.

Possible causes—insufficient optimization for a compositional XOR rule, recurrent initialization/optimizer choice, or sequence-length interaction—remain hypotheses; no learning curves or optimizer comparison were captured. Preserve v1 as run. Any change must receive a new outcome-informed version and a separate contract.

## Reproducibility

- Contract, runner, and verifier: [`model/M10_M5_EPROP_TEMPORAL_XOR_V1`](../../model/M10_M5_EPROP_TEMPORAL_XOR_V1/)
- Raw per-seed and summary outputs: [`data/results/M10_M5_EPROP_TEMPORAL_XOR_V1`](../../data/results/M10_M5_EPROP_TEMPORAL_XOR_V1/)
- Independent post-run verifier: `verify_m10.py`; status `PASS`
- Environment: Python 3.12.13, NumPy 2.4.4
- Seeds: 300–329; 6,000 training and 500 held-out episodes per seed × delay × arm
