# Superseded state-gating control run

The initial synthetic run used an arithmetic mean to set the no-gate control's sensory gain. Forward and reversal modes have unequal stationary occupancy, so this control changed both state dependence and average gain. It did not isolate the state gate and must not be cited as the primary result.

After inspecting the output, the control was corrected to use the stationary occupancy-weighted mean, and the experiment was rerun with the recorded design/seeds. The corrected result is published separately under `M2_STATE_GATED_GAIN_V1`; it is still post-result exploratory because correction followed output inspection. The original runner for this v0 archive is not present in the current source tree, so this package preserves the output and correction history without claiming exact rerun reproducibility.
