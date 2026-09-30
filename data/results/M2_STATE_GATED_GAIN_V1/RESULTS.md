# Experiment 2 results: motor-state-conditioned sensory gain

**Status:** completed post-result-corrected exploratory synthetic experiment with development-only coefficient selection and held-out test episodes. The no-gate control was corrected after inspection of the initial output to match stationary motor-mode occupancy; the correction history is documented in [`../EXPERIMENT2_CONTROL_CORRECTION.md`](../EXPERIMENT2_CONTROL_CORRECTION.md). This is not biological validation. The mode-dependent sensor-noise contrast is an explicit synthetic assumption, not a result established by the biological source.

## Main result

The selected gated controller learned coefficients `(g_F=0.25, g_R=0.0, α=0.25)`; the parameter-count-matched additive recurrent control selected `(w_x=0.25, w_q=0.0, α=0.25)`. In the held-out 12-cell grid, the gated controller exceeded the additive control in all 9 cells with target hazard `0.002`, `0.01`, or `0.04`, and was lower in all 3 high-volatility cells at hazard `0.12`.

At the development-like condition `h=0.01`, `σ_F=0.8`, `σ_R=2.4`, held-out mean accuracy was:

| Model | Accuracy |
|---|---:|
| State-gated feedback | 0.9709 |
| Parameter-count-matched additive recurrent control | 0.9387 |
| Gated model, no feedback | 0.8487 |
| Gated model, occupancy-matched no state gate | 0.9392 |
| Gated model, inverted gate | 0.6693 |
| Exact Bayesian observer with known task parameters | 0.9808 |

The paired accuracy difference between the gated model and additive recurrent control was `+0.0322` (95% episode-bootstrap interval `[+0.0298, +0.0346]`; 300 independent episodes). Relative to the occupancy-matched gate-destroyed model, the paired difference was `+0.0316` (95% interval `[+0.0290, +0.0343]`). The oracle Bayesian observer outperformed the gated model in this cell and throughout the 12-cell test grid.

At high volatility (`h=0.12`, `σ_F=0.8`, `σ_R=2.4`), the gated model reached `0.8606`, compared with `0.8676` for the additive control (paired difference `−0.0070`, 95% interval `[−0.0095, −0.0047]`). Feedback can be beneficial or harmful depending on target volatility, even when state-dependent observation reliability is built into the task.

## Interpretation

This experiment establishes a bounded computational result: **a state-conditioned sensory gain can outperform an equal-parameter additive recurrent controller when the task has mode-dependent evidence reliability and the target is not too volatile.** Removing or reversing the gate substantially reduces accuracy in most tested cells. The held-out high-volatility losses and the better Bayesian result limit any general superiority claim.

The advantage is conditional on the task construction: the reversal mode was made noisier by design. Ji et al. report that AIY thermosensory responses depend on locomotor state, but do not show that thermosensory measurement noise is higher during reversals. The experiment therefore tests a plausible computational consequence of state-dependent gating, not a direct biological fact. The selected controller also receives the motor-mode variable as an external input; it does not simulate a RIM relay or learn how that signal is generated.

## Post-result reliability-shift sensitivity

I held the development-selected parameters fixed and tested two additional task families: equal observation reliability in forward/reversal states, and reversed reliability where reversal observations are cleaner. These are explicitly post-result sensitivity tests, not confirmatory evaluations. In the equal-reliability condition at `h=0.01`, `σ_F=σ_R=0.8`, the fixed gated model scored `0.9713`, compared with `0.9782` for the additive recurrent controller and `0.9785` for the occupancy-matched recurrence with the gate removed. At the reversed-reliability condition (`σ_F=0.8`, `σ_R=0.4`), gated scored `0.9720` and additive scored `0.9804`. The gate advantage therefore depends on the synthetic mode/reliability relationship; it does not generalize to environments where that relationship is absent or reversed.

The full sensitivity sweep is in [`../reliability_shift_sensitivity/`](../reliability_shift_sensitivity/). This result narrows the claim: the operation is useful only when the task structure matches the gate. It strengthens the need to distinguish the directly observed biological state dependence from the unverified interpretation that the state signal reports sensory reliability.

## Provenance and reproducibility

- Contract fixed before this experiment's outputs: [`STATE_GATED_EXPERIMENT_CONTRACT.md`](../STATE_GATED_EXPERIMENT_CONTRACT.md).
- Implementation: [`run_state_gated_experiment.py`](../run_state_gated_experiment.py).
- Full episode-level test data: `episode_metrics.csv`.
- Per-cell estimates and paired intervals: `condition_summary.json`.
- Seeds, selected parameters, and resolved design: `run_manifest.json`.
- Development coefficients were selected on 200 episodes; each of 12 held-out cells used 300 new episodes.
- Episode is the statistical unit. Timesteps are repeated observations.
- Fixed-parameter reliability sensitivity, generated after the primary test: [`../reliability_shift_sensitivity/`](../reliability_shift_sensitivity/).

## Research consequence

The result justifies a stronger next comparison, not a claim of NMI-level completion: (1) separate the sensory-gain operation from motor-state persistence, (2) test robustness when the relation between motor mode and sensory reliability changes or disappears, (3) use parameter-matched learned recurrent networks and the task-optimal Bayesian reference, (4) add a closed-loop environment where actions alter sensory sampling, and (5) connect the artificial operations to the exact experimentally supported biological perturbations without treating anatomy as causal proof.
