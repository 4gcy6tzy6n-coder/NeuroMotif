# M9 — M5 teaching-event eligibility in a trainable recurrent model

**Version:** M9-v1. **Classification:** post-result exploratory AI study. The prior M5 synthetic outcomes are known. This is not confirmatory evidence, not a biological reanalysis, and not evidence that a cerebellar circuit uses the implemented rule.

## Question

In a new sequence-level delayed-association task, does a local synaptic eligibility approximation improve online learning over a one-step local update in a trainable leaky recurrent network, and how does it compare with exact backpropagation through time (BPTT) for the same architecture?

This task is separate from the previous per-timestep random-feature classification and contextual-bandit tasks. It does not use Fish1.5 structural results or claim that Fish1.5 recurrence predicts persistence.

## Task and independent unit

- Each task seed defines a fixed random permutation from four cue classes to four outcome classes using NumPy `default_rng(seed * 100003 + 17)`. Model initialization uses `default_rng(seed * 101 + 31)`.
- Each episode input is an array of shape `(D+1, 8)`. Time 0 contains a one-hot cue in dimensions 0–3 and zeros in dimensions 4–7. Each of the next D steps is an independent eight-dimensional Gaussian distractor with mean 0 and standard deviation 0.25. The label is the permuted cue class and is supplied only to the terminal learning update, never as an RNN input.
- Delays are fixed at `D ∈ {4, 16, 64}`. The target cue is the only task-relevant input; distractors are not predictive.
- For seed `s` and delay `D`, training episodes use `default_rng(s * 1000003 + D * 101 + 1)` and test episodes use `default_rng(s * 1000003 + D * 101 + 2)`. Each arm receives the same 500 training episodes and 250 held-out test episodes within each seed and delay. Hidden state resets at each episode.
- Thirty independent task seeds (`100..129`) define the statistical unit. Delays, episodes, and arms are paired/repeated observations within seed; they are not independent samples.

## Shared model

A fully trainable 24-unit leaky tanh RNN with 8 input dimensions and 4 output classes:

`h_t = (1 - λ) h_(t-1) + λ tanh(W_x x_t + W_h h_(t-1) + b)`, `λ = 0.1`.

`W_h` is initialized orthogonally at spectral radius 0.9; `W_x` is initialized from a zero-mean Gaussian with standard deviation 0.5; output weights use standard deviation 0.01. All arms start from identical seed-specific parameters. Training uses online single-episode updates, SGD learning rate 0.02, global gradient-norm clipping at 1.0, no momentum, and no weight decay. These settings are fixed, not selected using current-run outcomes.

## Frozen update arms

1. **ELIGIBILITY_TRACE:** at every time step accumulate local eligibility for each input, recurrent, and bias synapse using `e_t = 0.98 e_(t-1) + λ(1 - z_t²) × presynaptic_activity`, where `z_t = tanh(preactivation)`. At the teaching event, multiply each accumulated synaptic trace by the postsynaptic learning signal from the output error and update the recurrent model.
2. **NO_TRACE:** use only the local one-step eligibility at the teaching event, with the same architecture, data, initial weights, target signal, optimizer, and clipping.
3. **BPTT:** compute the exact gradient of the same terminal cross-entropy through the full episode for the same architecture and update with the same online SGD and clipping.

For every arm, the readout uses the ordinary terminal cross-entropy gradient. The local eligibility learning signal is `W_out.T @ (softmax(logits) - one_hot(target))`, computed from pre-update readout weights. In the trace and no-trace arms, hidden-weight updates use that signal times the specified local eligibility. The local rule is an explicit simplified e-prop-style abstraction, not a claim of exact equivalence to the biological plasticity rule.

## Outcomes and analysis

- Primary outcome: held-out classification accuracy.
- Primary contrast: `ELIGIBILITY_TRACE − NO_TRACE`, averaged equally across the three delays within each task seed, then across 30 task seeds.
- Report the paired task-seed bootstrap percentile 95% interval using 20,000 resamples from `default_rng(2026093009)`. Report the fraction of task seeds with a positive averaged contrast.
- Secondary comparisons: `ELIGIBILITY_TRACE − BPTT`, `NO_TRACE − BPTT`, and all per-delay means/contrasts. Do not pool test episodes as independent units.
- Numerical non-finiteness aborts the run and is recorded; no seeds or exclusions may be selected by performance.

## Interpretation and stop rule

A positive primary interval supports only a local eligibility advantage over the one-step update in this particular synthetic task and architecture. It does not establish superiority to BPTT, general task-family transfer, LNN/LTC performance, biological mechanism validation, or connectome transfer. The BPTT gap is always reported. A null or adverse result remains a valid exploratory outcome. Run once, preserve all outputs, and do not tune this task or these arms after outcomes are seen; any further optimization is a separately named post-result version.
