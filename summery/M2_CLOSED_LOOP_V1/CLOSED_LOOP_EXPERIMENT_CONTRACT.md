# Experiment 3: closed-loop target tracking with a trainable recurrent baseline

**Status:** exploratory computational experiment; no biological outcome data are used. The task is designed to move beyond one-step direction classification.  
**Biological anchor:** *C. elegans* AIY represents thermal and motor-state signals; motor-to-AIY corollary discharge requires RIM and contributes to forward-run persistence (Ji et al., 2021).  
**Synthetic assumptions:** position error is a proxy sensory signal; a forward/reversal mode is supplied as an external motor-state channel; observation noise differs by mode in one test regime. These are engineering choices, not direct claims from the worm experiments.

## Environment

- One-dimensional position `p_t ∈ [-5,5]`; goal `g_t ∈ {-3,+3}`.
- At the beginning of each step, the goal flips with hazard `h`; the observation is `x_t = g_t - p_t + ε_t`.
- The external motor context `q_t ∈ {F,R}` follows a two-state Markov chain: `P(F→R)=0.03`, `P(R→F)=0.20`. This is separate from movement direction.
- After choosing action `a_t ∈ [-1,1]`, position changes as `p_(t+1)=clip(p_t+0.15*a_t+η_t,-5,5)` with `η_t ~ Normal(0,0.01)`.
- Each episode runs 240 steps; each episode is the statistical unit. All policies share the same exogenous goal, motor-context, measurement-noise and process-noise random streams within a test cell.
- Test target-switch hazards: `{0.002, 0.02, 0.08}`. Test sensory conditions: (A) high reliability contrast `σ_F=0.2, σ_R=1.2`; (B) equal reliability `σ_F=σ_R=0.7`; (C) reversed reliability `σ_F=1.2, σ_R=0.2`. There are 300 independent episodes per cell.

## Policies

1. **Fixed gated feedback:** `a_t=tanh(0.6*(g(q_t)*x_t+0.2*a_(t-1)))`, with `g(F)=1`, `g(R)=0.15`.
2. **Occupancy-matched no gate:** same feedback, but fixed sensory gain `ḡ=g(F)P(F)+g(R)P(R)` based on the motor-context transition matrix.
3. **Gated sensory-only:** same gains with the previous-action feedback term removed.
4. **Ungated sensory-only:** same as a memoryless sensory controller with unit sensory gain and no feedback.
5. **Trainable GRU controller:** 16 hidden units; inputs are normalized sensory error, motor-context code, and previous action. It is trained with supervised imitation on 512 simulated training episodes to approximate the privileged proportional teacher `tanh(0.7*(g_t-p_t))`; optimizer Adam, learning rate 0.003, batch 32 episodes, 8 epochs, fixed seed. It receives no target, true position, future observations, or test outcomes.
6. **Privileged teacher reference:** uses true position error to choose `tanh(0.7*(g_t-p_t))`; this is an oracle reference, not a deployable policy.

## Outcomes

- Primary: episode mean absolute goal-position error (lower is better).
- Secondary: fraction of steps within `0.5` position units of the goal; after each target switch, movement-direction correction delay is the first step (within 40 steps) followed by three consecutive actions pointing toward the new target. Episodes without a switch have no delay value; unrecovered switches are censored at 40.
- Report paired episode bootstrap intervals (20,000 resamples) against the occupancy-matched no-gate controller and trained GRU.
- No gate status is assigned. This exploratory task can identify useful regimes and failure boundaries, not biological validity or publication-level generality.

## Limits

The model receives motor context directly; it does not model how RIM transmits the signal or how the animal generates reversals. The assumption that reversal measurements are noisier is unverified and is deliberately challenged by the equal and reversed reliability test regimes. The teacher is privileged and the GRU is a generic, trainable comparator; any performance difference must be reported with these asymmetries stated.
