# M8 — Truncated eligibility memory horizon frontier

**Classification:** post-result exploratory follow-up to M5/M7. Earlier eligibility-trace outcomes informed this question. This is an algorithmic boundary study on a synthetic random-feature classification task; it is not biological validation or an algorithm-novelty claim.

**Implementation correction:** the initial execution accessed the complete preloaded feature matrix when forming truncated windows, so it did not enforce the stated history-buffer boundary. Those outputs are retained under `results_v0_invalid_unbounded_history/` and excluded. The corrected runner uses only a per-horizon rolling buffer for eligibility updates. This correction was made after inspecting the initial run and is explicitly outcome-informed; the corrected execution is a post-result re-execution, not a pristine preregistered test.

## Question

Does retaining a longer bounded history of feature gradients improve delayed supervised credit assignment over an immediate-feature update, and how does that tradeoff vary with input autocorrelation and feedback delay?

## Fixed task and units

- Four-class classification with the M7 32-input, 64-feature random tanh teacher/readout family.
- AR(1) correlation `rho ∈ {0.0, 0.5, 0.9}`; delays `D ∈ {4, 16, 64}`.
- Thirty independent task seeds. The task seed is the inferential resampling unit; all rho, delay, horizon and arm conditions are paired within seed.
- 3,000 training and 1,000 fresh test examples per task; common task streams and labels across horizons within a seed/rho condition.
- Fixed learning rate `0.01`, discount `gamma=0.98`; no hyperparameter search.

## Update arms

- `HORIZON_1`, `HORIZON_4`, `HORIZON_16`, `HORIZON_64`: at label arrival, form the normalized exponentially weighted sum of the most recent `H` feature vectors, where the newest has lag zero and weight `gamma^lag`. The delayed prediction error is computed from the probabilities stored for the labeled example. The horizon buffer is the only history state used by that arm.
- `EXACT_REPLAY`: apply the delayed error to the feature vector from the labeled example; retained as a higher-memory reference.

All arms have the same 64×4 trainable readout and use the same labels, learning rate and delayed prediction error. The horizon arms differ in explicit stored history (`H × 64` float values). They are not claimed to be biologically measured trace equations.

## Primary estimand

For each task seed, average `accuracy(HORIZON_64) − accuracy(HORIZON_1)` equally over the nine rho × delay conditions. Report the mean and paired task-seed bootstrap 95% interval (20,000 resamples). Other horizons and cellwise values are prespecified descriptive analyses. Exact replay is always reported as the strong higher-memory comparator.

## Interpretation and stop rule

This tests whether a longer truncated feature-history state helps over an immediate-feature update within this task family. It does not establish superiority to exact replay, BPTT, trained recurrent models, other task families, or biological mechanisms. Report memory in stored float values as well as accuracy. Run this fixed grid once; do not tune gamma, horizons, learning rate, task, or select favorable cells after outcomes.
