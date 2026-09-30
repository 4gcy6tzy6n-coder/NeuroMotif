# M10 — Eligibility traces on delayed two-cue XOR integration

**Experiment ID:** `M10_M5_EPROP_TEMPORAL_XOR_V1`  
**Classification:** post-result exploratory artificial benchmark. M5/M7/M8/M9 outcomes were known before this task was specified.  
**Question:** In a trainable recurrent network, does a local eligibility trace improve online learning of a temporally separated two-cue XOR rule over an immediate one-step local update, and how does it compare with exact BPTT?

## Scope and claim boundary

This is a new synthetic task family relative to M9's one-cue delayed association and M7/M8's random-feature readout family. It tests temporal binding and delayed credit assignment in an artificial recurrent network. The biological motivation is the bounded cerebellar climbing-fiber teaching-event literature; the trace equation is a computational abstraction, not a measured biological synaptic rule. No biological data are used. This is not LNN/LTC, biological validation, or connectome-to-AI transfer.

## Task, data generation and units

- Each episode contains two binary cues `(a,b)`, sampled independently and uniformly from `{0,1}`. The target is `y = a XOR b`, with two balanced classes in expectation.
- Input has four channels. At `t=0`, the first cue is one-hot in channels 0–1. Steps `t=1..D` contain independent, uninformative Gaussian distractors on all four channels (`mean=0`, `SD=0.25`). At `t=D+1`, the second cue is one-hot in channels 2–3. At `t=D+2`, input is zero and the network emits the terminal prediction. The fixed delays are `D ∈ {4,16,64}`.
- For each seed and delay, all arms receive the identical 6,000 training episodes and 500 held-out test episodes, in identical order. Episode state resets between examples. The task seed is the independent unit; examples, delays and arms are paired/repeated observations within seed.
- Thirty task seeds are `300..329`, disjoint from M9 seeds. Task streams use `default_rng(seed*1000003 + delay*101 + split_code)` with split codes 1 (train) and 2 (test); initialization uses `default_rng(seed*101 + 31)`.
- Training and test pairs are sampled from the four possible `(a,b)` combinations; no example is excluded based on outcomes or model performance.

## Shared model and optimizer

A fully trainable 24-unit leaky tanh RNN with 4 inputs and 2 outputs:

`h_t = 0.9 h_(t-1) + 0.1 tanh(Wx x_t + Wh h_(t-1) + b)`.

`Wh` is orthogonal with spectral radius 0.9; `Wx ~ Normal(0,0.5)`; output weights use `Normal(0,0.01)`; biases start at zero. All arms share identical seed-specific initial parameters, task examples, online SGD (`learning_rate=0.02`), and global gradient-norm clipping at 1.0. No momentum or weight decay. There is no hyperparameter search.

## Frozen update arms

1. `ELIGIBILITY_TRACE`: at every step accumulate local eligibility for input, recurrent and bias weights with decay `gamma=0.98` and local factor `0.1*(1-tanh(preactivation)^2)*presynaptic_activity`. At the terminal error, multiply accumulated eligibility by the output-derived hidden learning signal.
2. `NO_TRACE`: use only the final step's one-step local eligibility, with all other settings identical.
3. `BPTT`: exact terminal cross-entropy gradient through the same full sequence and same parameter set, online SGD and clipping.

The trace is a simplified e-prop-style learning approximation. It is not claimed to implement the unique biological mechanism or to be mathematically equivalent to BPTT.

## Outcomes and frozen analysis

- Primary outcome: held-out XOR classification accuracy.
- Independent unit: task seed (`n=30`). No episode, delay, frame, or network state is treated as an independent replicate.
- Primary contrast: `ELIGIBILITY_TRACE − NO_TRACE` in accuracy, first averaged equally over the three delays within each seed, then over seeds. Report mean, paired task-seed percentile bootstrap 95% interval (20,000 resamples; seed `2026093010`), and positive-seed count.
- Required comparator: report `ELIGIBILITY_TRACE − BPTT` and `NO_TRACE − BPTT` with the same paired seed bootstrap.
- Per-delay contrasts and BPTT viability are secondary fixed outputs. A delay is viable only when the BPTT seed-bootstrap 95% lower bound exceeds binary chance (0.50). If any delay fails, the all-delay primary conclusion is `INCONCLUSIVE_TASK_NOT_LEARNABLE_ACROSS_GRID`; retain all results without excluding that delay.
- No p-value, multiplicity-selected endpoint, or favorable delay subset will be used to upgrade the primary result. No inference extends beyond this task family and architecture.

## Preflight, run integrity and stop

Before outcomes are computed, run the implementation preflight: verify finite-difference agreement of BPTT gradients on a deterministic toy episode, dimensions, finite parameter initialization, task-label truth table and input timing. Save source/contract hashes and environment to `M10_PREFLIGHT.json`. Then run once. No tuning, rerun, seed replacement, or task change is allowed within v1. Any later change requires a separately identified, explicitly outcome-informed version and preserves all v1 outputs.
