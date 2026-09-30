# M2 action-feedback pilot

**Status:** completed exploratory synthetic experiment.

## Result

The task used a binary target that changed with a specified hazard and observations with Gaussian noise plus persistent contradictory bursts. With fixed feedback strength `α=1` versus no feedback `α=0`, accuracy was higher in eight of the nine tested hazard–noise cells. The exception was low noise with the highest switch hazard, where accuracy decreased. Episode was the independent unit; time steps were not treated as independent observations. The same seeded episode stream was paired across controller settings.

## Boundary

This is a synthetic scalar-controller result. It does not validate the *C. elegans* circuit, establish a general AI benefit, or compare against an optimal observer or trained recurrent model. The later boundary extension and Bayesian comparisons are separate follow-up rounds.

## Provenance

The archived episode table, condition summary, and run manifest are in `data/results/M2_ACTION_FEEDBACK_PILOT_V1/`. The public runner preserves the simulator and seed logic but writes each rerun to a unique UTC timestamped subdirectory under that result folder. The run manifest records NumPy 2.4.4; historical Python version was not captured.
