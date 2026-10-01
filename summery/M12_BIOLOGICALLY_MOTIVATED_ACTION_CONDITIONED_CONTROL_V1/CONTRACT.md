# M12 — biologically motivated motor-state feedback in closed-loop tracking

**Code:** `M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1`
**Status:** outcome-informed synthetic transfer study; freeze before generating M12 outputs.
**Route:** B, *C. elegans* cell-class-level published motor-state feedback → artificial controller.
**Prior knowledge:** M2 outcomes are known. This is a new task family and architecture-level transfer test, not a confirmatory replication and not biological validation.

## Biological computation and boundary

Ji et al. report that locomotor-state feedback requiring RIM shapes AIY activity and is associated with persistence of forward runs during thermotaxis. The transferred computation is narrowly represented as **motor-state input modulates sensory updating while an internal state carries information forward**. The published work does not identify the unique synaptic carrier, an exact machine-learning equation, or an AI benefit. The permitted identity granularity is cell class only (AFD/AIY/RIM); M12 contains no animal data and makes no new biological claim.

Primary biological source: Ji et al. (2021), *eLife*, https://elifesciences.org/articles/68848.

## Question

In a closed-loop moving-target tracking task where the controller's own movement changes sensory reliability, does an explicitly motor-state-gated recurrent controller reduce held-out tracking error relative to a parameter-matched generic GRU, and does removing or permuting its motor-state input remove any advantage?

This is an engineering transfer question. Because the generator makes action state informative about observation precision, the task tests a stated boundary condition of the abstraction; it does not show that worms use this task or that AIY implements this exact rule.

## Task generator

- One-dimensional target location `q_t` follows an AR(1) process: `q_t = 0.97 q_(t-1) + η_t`, with `η_t ~ Normal(0, 0.08²)`.
- The controller position is `p_(t+1) = p_t + u_t`, with `u_t ∈ [-0.25, 0.25]`.
- At time `t`, the observation is relative position plus noise: `y_t = q_t - p_t + ε_t`. The observation standard deviation is `σ_t = 0.05 + κ |u_(t-1)|`, with episode-level `κ ~ Uniform(0.25, 0.75)`. The value of `κ` is provided to every learned arm; the previous action is the motor-state/efference-copy signal and determines current sensory reliability.
- Episodes have 256 steps. Initial target is sampled from a Gaussian with mean 0 and variance `1/3`; initial controller position is sampled from `Uniform(-1,1)`; initial previous action is zero. The same task seed determines paired training episodes and all arms' initialization/data order; test trajectories use disjoint seeds.
- A known-generator Kalman observer paired with a fixed-gain chase policy is a demonstration/reference controller, not an optimal controller: action affects future observation noise, so the full problem has a dual-control component. A memoryless reactive policy is the task-viability floor.

## Frozen arms

1. **MOTOR_GATED_RNN:** 7-unit recurrent controller. At each step its carry gate and sensory-update gate are `a_t = sigmoid(W_a [h_(t-1), u_(t-1), κ] + b_a)` and `g_t = sigmoid(W_g [h_(t-1), u_(t-1), κ] + b_g)`; its candidate state is `c_t = tanh(W_x [y_t, p_t, u_(t-1), κ] + W_h h_(t-1) + b_x)`. The update is `h_t = a_t ⊙ h_(t-1) + (1-a_t) ⊙ (g_t ⊙ c_t)`. A linear readout followed by `tanh` and scaling to `[-0.25,0.25]` produces the action.
2. **GENERIC_GRU:** 6-unit GRU receiving exactly the same four inputs `[y_t, p_t, u_(t-1), κ]`, followed by the same bounded action readout. Under the specified dense parameterization, MOTOR_GATED_RNN has 232 trainable parameters and GENERIC_GRU has 223 (4.0% difference). The runner must verify these counts before training; otherwise stop as `INVALID_IMPLEMENTATION` and resolve the mismatch without inspecting outcomes.
3. **MOTOR_ZERO_ABLATION:** same MOTOR_GATED_RNN architecture and parameter count, but previous-action input is fixed to zero during both training and evaluation.
4. **MOTOR_PERMUTED_ABLATION:** same architecture and parameter count; previous-action values are permuted across episodes independently at every time step within each training minibatch and within the test rollout batch. This preserves each time point's batch marginal while breaking the per-trajectory relation. The true action still drives the plant and sets its observation noise; only the action value supplied to this model is permuted.
5. **KALMAN_LQG_REFERENCE** and **MEMORYLESS_REACTIVE_REFERENCE:** non-learned diagnostic controllers.

The demonstration controller maintains the scalar Kalman estimate for `q_t`, which is an exact posterior under the task's Gaussian state/observation model: `q_0 ~ Normal(mean=0, variance=1/3)`; for later steps, predict with `φ=0.97` and process variance `0.08²`, then update from `y_t+p_t` using observation variance `(0.05+κ|u_(t-1)|)²`. Its action is `clip(0.7*(qhat_t-p_t), -0.25, 0.25)`. It is a fixed-gain chase policy, not a Bayes-optimal policy for the action-dependent observation process. The reactive reference uses the same proportional action rule with `qhat_t` replaced by the current noisy position estimate `y_t+p_t`.

All learned arms use identical demonstration trajectories from the Kalman observer/fixed-gain chase controller, identical episode-seed blocks, and identical optimization budgets: 256 training episodes per seed, full 256-step sequence training, mean squared action imitation loss, Adam (`lr=0.003`), batch size 16 episodes, and exactly 30 epochs. Use the final epoch weights; no checkpoint selection, early stopping, or hyperparameter search is allowed. The two neural arms satisfy the parameter-match rule above; other ablations retain the full parameter count but have the motor path disabled or misaligned.

## Units, split, endpoints, and analysis

- Independent unit: task-seed block (not time step or episode). Use 40 paired blocks, seeds `812000..812039`.
- Per seed, generate 256 demonstration episodes for training and 128 test episodes per arm; use disjoint latent trajectories for train and test. Each episode contributes one mean squared tracking error over its 256 time steps.
- Primary endpoint: test closed-loop normalized tracking MSE, normalized by the known stationary target variance `0.08²/(1−0.97²)`, and averaged equally over test episodes within each seed.
- Primary contrast: `MOTOR_GATED_RNN − GENERIC_GRU` in per-seed endpoint; negative favors the gated model. Report paired mean difference and a 95% percentile bootstrap CI over 40 seed blocks (20,000 resamples; analysis seed `812999`).
- Secondary prespecified contrasts: gated vs zero-input ablation; gated vs permuted-input ablation. Apply Holm correction to the two secondary tests only. Report per-seed paired differences and CIs. Do not use secondary outcomes to replace the primary contrast.
- Report Kalman-observer/fixed-gain and reactive-reference performance as task diagnostics. Report within-episode action standard deviation, sign-switch rate, and episode-level failure/divergence counts descriptively. A rollout fails if an error or position is nonfinite, or if absolute tracking error exceeds 5 for 10 consecutive steps. Do not pool frames as independent units.
- Meaningful-effect threshold: require the primary gated-vs-GRU reduction to be at least 2% of the generic GRU's mean normalized MSE, in addition to a 95% CI wholly below zero, to call a practically relevant advantage. This threshold is fixed before M12 outcomes.

## Viability, validity, and disposition

- Task viability passes only if the Kalman-observer/fixed-gain reference improves normalized MSE over the reactive reference by at least 10% on the generated test set and neither reference has more than 1% failed episodes.
- If viability fails: `M12 = INCONCLUSIVE_TASK_VIABILITY_FAILED`; do not tune v1.
- If parameter match, seed pairing, output integrity, or independent-unit checks fail: `M12 = INVALID_IMPLEMENTATION`; preserve artifacts, repair only implementation and rerun under a new version.
- If viable and the primary CI is wholly below zero and meets the 2% threshold: bounded support for this biologically motivated architecture on this generator. If the CI crosses zero or misses the threshold: no practically relevant advantage established. If wholly above zero: bounded disadvantage.
- A positive primary result without both secondary ablation contrasts supporting the motor path is **not** classified as mechanism-specific transfer.
- No route is allowed to change after viewing outcomes; apply this disposition table literally.

## Reproducibility and provenance

Before execution save the resolved environment, source hash, contract hash, generated-config hash, and all fixed seeds under the result directory. Persist episode-level train/test metrics (one row per seed × episode × arm), per-seed summaries, model parameter counts, training logs, and a machine-readable summary. A separate verifier must recompute output hashes, uniqueness/completeness of seed and episode keys, parameter-match compliance, and summary arithmetic without retraining. Do not include raw frames as independent observations.

## Interpretation limits

M12 is a post-result-informed synthetic test. A positive outcome supports only a bounded engineering result on this task. It cannot validate the worm mechanism, establish a unique RIM→AIY carrier, overcome E4-v1's public-data schema blocker, or support a cross-species motif claim. A null/adverse result closes this implementation on this generator; it does not falsify published worm biology.
