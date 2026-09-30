# Experiment 2 control correction record

The initial state-gating implementation compared the gated model with a no-gate model that replaced `g_F` and `g_R` by their arithmetic mean. The two motor modes do not occur equally often under the frozen transition probabilities, so this changed the average sensory gain as well as removing state dependence. That comparison did not isolate the gate.

I preserved that first run in:

- `state_gated_experiment_v0_arithmetic_mean_control/`
- `reliability_shift_sensitivity_v0_arithmetic_mean_control/`

The corrected no-gate baseline uses the stationary occupancy-weighted gain. For `P(F→R)=0.03` and `P(R→F)=0.20`, the stationary occupancies are `P(F)=0.20/0.23` and `P(R)=0.03/0.23`. The corrected control uses `ḡ=g_F P(F)+g_R P(R)`. The state-gated experiment and fixed-parameter reliability sensitivity were rerun from the same recorded seeds, and the corrected data now live in the active result directories.

Because this correction followed inspection of the initial run, the corrected experiment is classified as **post-result exploratory**. Do not present it as a clean preregistered confirmation. The unchanged data-generating process and test episode seeds do not erase the analysis history.
