# Experiment 2: state-gated sensory evidence under motor-state-dependent reliability

**Status:** frozen before Experiment 2 outcomes; synthetic computational experiment.  
**Biological inspiration:** AIY activity in *C. elegans* is motor-state dependent; thermosensory responses are observed during forward runs and suppressed during reversals, while a motor-to-AIY corollary-discharge pathway requires RIM (Ji et al. 2021).  
**Explicit synthetic assumption:** this experiment makes observations less reliable during the reversal state. The cited study does not establish that sensory measurement noise is higher during reversals. This assumption defines a test environment, not a biological fact.

## Question and directional hypothesis

Does an explicit motor-state-conditioned sensory gain improve sequential direction decisions when evidence reliability differs by motor state, beyond a parameter-count-matched additive recurrent controller? Does destroying state gating remove that advantage? A fixed `α` action-feedback term is predicted to help when current evidence is unreliable, but may impair tracking when target direction changes quickly. The exact Bayesian observer, given the true generative parameters, is expected to perform at least as well as any restricted controller; no prediction of beating it is made.

## Synthetic environment

- Episode length: 400 steps; each episode is one independent unit.
- Hidden target direction `d_t ∈ {-1,+1}` starts at `+1` and flips with hazard `h` per step.
- Motor mode `q_t ∈ {F,R}` starts at forward `F`; transition probabilities are `P(F→R)=0.03` and `P(R→F)=0.20` per step.
- Observation: `x_t = d_t + Normal(0, σ_q)`, with mode-specific noise `σ_F` or `σ_R`.
- Development set: 200 episodes at `h=0.01`, `σ_F=0.8`, `σ_R=2.4`.
- Test grid: `h ∈ {0.002, 0.01, 0.04, 0.12}` crossed with `σ_F ∈ {0.5, 0.8, 1.2}` and `σ_R=σ_F+1.6`; 300 fresh episodes per cell.
- Fixed master seed `20261001`; independent child streams are assigned to the development set and each test cell, with episodes drawn sequentially from their cell stream. All models share the same generated episode within each comparison.

## Models

All recurrent controllers emit `a_t = sign(u_t)`, with ties resolved to `+1`.

**State-gated feedback model:**

```text
u_t = g(q_t) * x_t + α * a_(t-1)
g(F)=g_F; g(R)=g_R
```

**Parameter-count-matched additive recurrent control:**

```text
u_t = w_x * x_t + w_q * m(q_t) + α * a_(t-1)
m(F)=+1; m(R)=-1
```

Each architecture has three scalar coefficients. Development-set grid search selects coefficients from 512 combinations per architecture: sensory/gain coefficients `{0, .25, .5, .75, 1, 1.25, 1.5, 2}`, mode coefficient `{−1, −.5, −.25, 0, .25, .5, 1, 1.5}`, and feedback `α ∈ {0, .25, .5, .75, 1, 1.25, 1.5, 2}`. The `g_F,g_R` pair uses the sensory/gain grid. Ties resolve by the lexicographically first grid tuple. The development set is used only to choose these fixed coefficients.

Frozen counterfactuals reuse the selected gated-model coefficients: (1) `NO_FEEDBACK`, set `α=0`; (2) `NO_GATE`, replace both mode gains by the mode-occupancy-weighted mean `g_F*P(F)+g_R*P(R)`, where stationary occupancy follows the declared mode-transition matrix; (3) `INVERTED_GATE`, swap `g_F` and `g_R`. The additive recurrent control is tuned independently on the same development set under the same grid size.

**Exact Bayesian observer:** filters the two-state Markov target using the known hazard and current motor-mode-specific Gaussian likelihood. This is an oracle-parameter algorithmic reference, not a learned/capacity-matched architecture.

## Analysis correction history

The first implementation used the unweighted arithmetic mean for `NO_GATE`. After inspecting that run, I recognized that forward and reversal modes have unequal stationary occupancy. I corrected the no-gate control to use the transition-matrix-weighted mean gain and reran the test grid. The original files are preserved under `state_gated_experiment_v0_arithmetic_mean_control/` and labeled superseded. Because the control correction followed initial outcome inspection, the corrected run is explicitly **post-result, exploratory**, not confirmatory, despite the unchanged fixed parameter-selection grid and test seeds. The correction and its rationale are documented in `EXPERIMENT2_CONTROL_CORRECTION.md`.

## Outcomes and analysis

- Primary outcome: per-episode proportion of steps with `a_t=d_t`.
- Secondary diagnostic: action switch rate per step.
- Report per-cell mean, SD across episodes, and paired 95% bootstrap intervals (20,000 episode resamples) for the gated model against each counterfactual and the additive recurrent control.
- No timestep is treated as an independent sample. Test data are not used to select parameters.
- This is a synthetic mechanism experiment. Results cannot validate the biology, identify a real neural circuit equation, or demonstrate broad AI benefit.

## Stop and interpretation

No threshold-based PASS is assigned in this exploratory-to-prospective computation study. Report the full test grid, including negative cells. A positive finding requires the state-gated model to beat both its gate-destroyed and parameter-count-matched additive controls on independent test episodes, with the preregistered intervals and boundary cells shown. Beating the oracle is neither expected nor required; a large oracle gap indicates that the simple mechanism is an inefficient solution for this task.
