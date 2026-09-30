# M2 targeted gain-optimization follow-up

**Status:** `POST_RESULT_ENGINEERING_EXPLORATION_CONTRACT_FROZEN_BEFORE_RUN`. This study was selected after the negative M2 results and is explicitly outcome-informed. It cannot be described as confirmatory, preregistered, or biological-to-AI transfer.

## Question

After the fixed reversal gain failed, can a learnable state-specific sensory gain improve target-tracking error when mode reliably predicts observation noise, compared with an equally sized generic recurrent controller trained directly on the control objective?

The intended optimization is narrow: determine whether the previous negative result reflects an overly rigid, imitation-trained gain rule in the high-reversal-noise regime. It does not optimize across papers or biological outcomes.

## Simulator and training distribution

- Use the same one-dimensional closed-loop simulator as `CLOSED_LOOP_EXPERIMENT_CONTRACT.md`: target values ±3, position bounds ±5, action gain 0.15, process-noise SD 0.01, horizon 160 for training and 240 for evaluation.
- Keep F→R / R→F transitions at 0.03 / 0.20.
- Each training batch samples target-switch hazard log-uniformly from `[0.002, 0.08]` and uses the already known high-reversal-noise mapping `sigma_F=0.2`, `sigma_R=1.2`.
- Training minimizes mean episode MAE directly by differentiating through the closed-loop simulator. This replaces privileged-teacher imitation for both policies.
- Ten independent training seeds; 200 Adam updates per model seed, batch 64 episodes, learning rate 0.01. Gated and generic policies receive the same exogenous batch for each paired seed/update.

## Parameter-matched policies

Each learned controller has exactly three trainable scalar parameters.

1. `LEARNED_MODE_GAIN`: mode-specific positive sensory gains `(gain_F, gain_R)` and positive previous-action coefficient. `action=tanh(gain_q * observation/5 + w_action * previous_action)`.
2. `LEARNED_GENERIC_CONTEXT`: positive global sensory gain, positive previous-action coefficient, and an additive mode-context bias. `action=tanh(w_sensory * observation/5 + w_action * previous_action + w_mode * mode_code)`.

The contrast tests multiplicative, mode-specific sensory gain against an additive generic use of the same mode input with the same parameter count. It does not compare against an RNN family or establish a universally fair architecture ordering.

Two unchanged fixed policies (`FIXED_GATED`, `FIXED_NO_GATE`) are retained only as secondary reference points. The privileged teacher is omitted from the primary comparison.

## Evaluation and outcomes

- Primary evaluation uses two previously unused switch hazards: `0.005` and `0.04`, under the high-reversal-noise mapping. Use 500 common-random-number episodes per cell and per training seed.
- Sole primary outcome: episode mean absolute target-position error. Sole primary contrast: `LEARNED_MODE_GAIN − LEARNED_GENERIC_CONTEXT`; negative values favor the mode-specific gain.
- Secondary descriptive stress conditions evaluate the same fixed trained controllers at the equal-noise and reversed-noise profiles for the same two hazards. These do not alter the primary result or select a revised gate.
- The 10 model-training seeds and shared test-episode IDs are separate crossed sources of variation. The primary 95% interval uses 20,000 crossed bootstrap replicates, resampling model seeds and common episode IDs separately.
- Episode is the rollout unit; frames and time steps are not independent observations.

## Interpretation and stop rule

- Entirely negative primary interval: optimized mode-specific gain reduces MAE relative to the parameter-matched additive-context controller in this specific high-reversal-noise simulator and hazard grid.
- Entirely positive interval: it increases MAE.
- Interval spanning zero: inconclusive.

Any favorable result remains post-result, task-specific engineering evidence. The noise mapping and motivation were selected after earlier outcomes; the hazard grid is held out but the simulator family is not. Do not call it biological transfer, general AI benefit, or evidence of neural causality. Preserve stress-condition failures. Do not continue tuning after reporting this run.
