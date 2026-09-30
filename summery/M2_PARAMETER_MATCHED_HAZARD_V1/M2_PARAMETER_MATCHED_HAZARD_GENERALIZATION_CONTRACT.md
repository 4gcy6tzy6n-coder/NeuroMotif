# M2 parameter-matched hazard-generalization follow-up

**Status:** `POST_RESULT_EXPLORATORY_CONTRACT_FROZEN_BEFORE_THIS_RUN`  
**Scope:** synthetic controller comparison only. The question and implementation are outcome-informed by the prior M2 pilot, fixed-gate, closed-loop, and DAgger results. This cannot be represented as a preregistered or confirmatory biological-to-AI transfer test.

## Question

Does explicit mode-dependent sensory gating improve closed-loop target tracking over a generic recurrent controller with the same two trainable scalar parameters, when tested on previously unused target-switch hazard values?

This isolates one artificial operation in the existing simulator. It does not test whether that operation is the biological mechanism, and the synthetic mode/noise relationship is not asserted to describe *C. elegans*.

## Simulator and fixed elements

- Reuse the closed-loop simulator equations and outcome definitions in `CLOSED_LOOP_EXPERIMENT_CONTRACT.md`.
- Keep horizon 240, goal values ±3, position bounds ±5, action gain 0.15, process-noise SD 0.01, and mode transitions F→R 0.03 / R→F 0.20.
- Preserve common exogenous goal, mode, measurement-noise, process-noise, and initial-position streams across policies within each evaluation cell.
- Use training horizon 160. Each training episode independently draws hazard log-uniformly from `[0.002, 0.08]`, and forward/reversal sensory-noise SDs independently uniformly from `[0.2, 1.2]`.
- The previous-action teacher is privileged: `tanh(0.7 * true_position_error)`. Teacher imitation is used only to fit both learned controllers.

## Controllers

All non-oracle policies use the same two-parameter form and therefore have exactly two trainable parameters (`w_sensory`, `w_action`):

```text
action = tanh(w_sensory * effective_observation + w_action * previous_action)
```

- `FIXED_GATED`: existing constants (`w_sensory=3`, `w_action=0.12`) and sensory gain 1.0 in F / 0.15 in R, with observation normalized by 5.
- `FIXED_NO_GATE`: same coefficients, occupancy-weighted constant gain using the frozen F/R transition probabilities.
- `LEARNED_GATED`: same gated input transform as `FIXED_GATED`; learn the two coefficients by DAgger-style teacher imitation.
- `LEARNED_NO_GATE`: same constant-gain transform as `FIXED_NO_GATE`; learn the same two coefficients using the same DAgger procedure and training episode streams.
- `PRIVILEGED_TEACHER`: reference only; sees true target error and is not a fair deployable comparator.

No GRU is included in this experiment. The parameter-matched comparison is between the two scalar recurrent controllers; it does not establish superiority over generic recurrent networks as a class.

## Training and held-out evaluation

- Train 10 independent seeds, each with 1,024 training episodes and four DAgger rounds. At each round collect on-policy states from the current policy, label them with the privileged teacher, and refit on the accumulated data. Both learned policies use identical seeds, episode counts, optimizer, batches, and epochs.
- Evaluate at switch hazards `0.005` and `0.04`, not used as fixed training conditions. For each hazard, test the three previously defined noise profiles: high reversal noise `(0.2, 1.2)`, equal noise `(0.7, 0.7)`, and reversed noise `(1.2, 0.2)`.
- Use 300 shared-stream evaluation episodes per hazard × noise cell and training seed. The 6,000 episode-seed-cell records per learned controller are repeated task simulations, not independent biological samples.
- Random seeds, training manifests, code and outputs are written before reporting outcomes. Existing simulator results have already been inspected, so the entire follow-up remains exploratory regardless of this new holdout.

## Outcomes and analysis

- Sole primary outcome: episode mean absolute target-position error (lower is better).
- Sole primary contrast: `LEARNED_GATED − LEARNED_NO_GATE`, averaged equally across the six held-out environment cells and then across training seeds. Negative values favor the gated controller.
- Independent replication level for controller fitting: training seed. Evaluation episodes are nested within seed and environment cell. Report the mean paired contrast and a hierarchical percentile bootstrap (resample training seeds, then paired episodes within each of the six cells; 20,000 draws).
- Report each cell's paired contrast and 95% interval descriptively. Fixed-gate contrasts, target-zone fraction, and switch delay are secondary and do not determine the primary interpretation.
- Do not calculate or select a second primary metric after seeing results. Do not pool frames or time steps as independent units.

## Interpretation

- If the primary 95% interval is entirely below zero: the two-parameter gated scalar controller has lower error on this specified held-out hazard grid, within this simulator and training procedure.
- If entirely above zero: it performs worse on that grid.
- If it includes zero: the comparison is inconclusive at the declared interval criterion.

None of these outcomes validates a biological motif, establishes causal circuit equivalence, demonstrates robustness outside this task generator, or supports population-level neural claims. No result will be combined with Fish1.5, *C. elegans*, or RR19 as if they shared one estimand.

## Stop condition

After this run and integrity/schema verification, update the M2 status and stop this follow-up. Do not tune the architecture or task based on its outcome. Any subsequent model family or task requires a separately labeled, outcome-informed study.
