# M2 pilot boundary extension

## Result

This post-pilot exploratory extension tested action-feedback strengths across target-switch hazards 0.08, 0.16, and 0.32, three sensor-noise levels, and 100 paired episodes per hazard/noise condition. The independent unit is the synthetic episode; the run contains 5,400 episode-by-alpha rows.

The extension locates a clear failure regime for a fixed positive feedback value. At hazard 0.32 and noise SD 0.5, accuracy was 0.8830 for no feedback (α=0) and 0.8111 for α=0.75, as recorded in the prior combined pilot analysis. Under hazard 0.08 and noise SD 1.5, the condition summary reports accuracy 0.71985 at α=0 and 0.76865 at α=1.0. These examples show the persistence–responsiveness tradeoff depends on task volatility and evidence noise; they do not identify an unbiased optimal α.

## Interpretation

The data support only a narrow synthetic conclusion: action-state feedback can help in some noisy, slowly changing regimes and can hurt when the target changes rapidly while observations are relatively clean. This boundary extension was run after the initial pilot, so it is exploratory rather than confirmatory. The simple scalar controller is not a faithful implementation of the published AFD–AIY/RIM circuit and does not establish a general AI inductive bias. A task-specific exact Bayesian observer was stronger than both simple controllers in every cell of the initial sweep; this extension does not reverse that result.

## Reproducibility and limitations

- Archived data are copied byte-for-byte from the local experiment outputs.
- `run_boundary_sweep.py` uses the same `simulate_episode` implementation in `run_pilot.py`; the release scripts change only output routing to timestamped repository-local folders.
- Episode streams are paired across feedback values within each condition; episode, not time step, is the independent unit.
- The manifest records seed, horizon, hazards, noise, feedback values, and row count, but not historical Python/NumPy versions or a dependency lock.
- This is an exploratory computational result, not biological validation or an independent-animal experiment.
