# M10 — Delayed two-cue XOR integration

**Classification:** post-result exploratory synthetic recurrent-network benchmark; not biological validation or general AI transfer.

Primary task-seed contrast (`ELIGIBILITY_TRACE − NO_TRACE`, equal mean over delays): **-0.0003** accuracy (95% bootstrap CI [-0.0021, +0.0017]); 8/30 task seeds positive.

Equal-delay mean held-out accuracy:
- ELIGIBILITY_TRACE: 0.5009
- NO_TRACE: 0.5012
- BPTT: 0.5009
- ELIGIBILITY_TRACE − BPTT: +0.0000 (95% CI [-0.0011, +0.0013])
- NO_TRACE − BPTT: +0.0004 (95% CI [-0.0012, +0.0018])

| Delay | Trace accuracy | No-trace accuracy | BPTT accuracy | Trace − no-trace (95% CI) |
|---:|---:|---:|---:|---:|
| 4 | 0.5065 | 0.5069 | 0.5067 | -0.0003 [-0.0019, +0.0009] |
| 16 | 0.5009 | 0.5012 | 0.5009 | -0.0003 [-0.0019, +0.0014] |
| 64 | 0.4953 | 0.4957 | 0.4950 | -0.0004 [-0.0051, +0.0051] |

BPTT task viability across the delay grid: **FAIL** (lower 95% seed-bootstrap bound must exceed 0.50 at every delay).

Task seeds are the independent units; examples and delays are repeated/paired. This experiment tests an artificial two-cue XOR sequence in one leaky tanh RNN. Eligibility is a simplified local teaching-signal abstraction; this is not a liquid neural network, biological validation, or connectome transfer.

## Analysis and failure experience

All three arms remained near binary chance across every delay. BPTT mean accuracy was 0.5067 at D=4 (95% seed-bootstrap interval [0.4979, 0.5157]), 0.5009 at D=16 ([0.4929, 0.5085]), and 0.4950 at D=64 ([0.4879, 0.5018]). The frozen task-viability criterion failed at all delays because none of the lower bounds exceeded 0.50. Accordingly, `M10_V1 = INCONCLUSIVE_TASK_NOT_LEARNABLE_ACROSS_GRID`; the near-zero trace-minus-no-trace estimate is not interpretable as evidence that eligibility does or does not help on a learnable XOR task.

The finite-difference check and output audits support implementation integrity, but they do not explain the task-learning failure. Possible explanations include insufficient optimization for a compositional two-cue rule, the selected recurrent initialization/optimizer, or an interaction of sequence length with the architecture. These are hypotheses only: this run did not store learning curves or compare alternative optimizers. No explanation was selected after the fact as established.

**Failure experience:** task viability must be demonstrated before interpreting a learning-rule contrast. A correct gradient implementation can still yield an unlearnable benchmark under the frozen training budget. Preserve all v1 outputs. Any task or optimizer change must be a separately labeled outcome-informed v2 with its own pre-run contract and disjoint task seeds.

## Verification

The pre-run BPTT finite-difference check had maximum absolute error `1.31e-10`. An independent post-run verifier confirmed 270 unique seed×delay×arm rows, 30 paired seed summaries, finite bounded metrics, exact recomputation of primary/per-delay/bootstrap statistics, recomputation of the viability gate, and agreement of source/result hashes. Verifier status: `PASS`; experiment status: `INCONCLUSIVE_TASK_NOT_LEARNABLE_ACROSS_GRID`.
