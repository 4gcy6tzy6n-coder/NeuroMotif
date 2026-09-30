# M2 state-gated sensory gain

## Design and result

The synthetic task compared a three-parameter motor-state-gated sensory-gain controller with a three-parameter additive recurrent control, plus feedback removal, gate removal, inverted gating, and a task-informed Bayesian reference. Coefficients were selected on a development set; the held-out grid covered 12 hazard/noise cells with 300 episodes per cell. Episode was the independent unit.

At the development-like held-out cell (hazard 0.01, σF=0.8, σR=2.4), the archived report gives accuracy 0.9709 for the gated controller, 0.9387 for the parameter-count-matched additive controller, 0.9392 for the occupancy-matched no-gate control, and 0.9808 for the exact Bayesian observer. Across the grid the gate exceeded the additive controller in nine cells and was lower in all three hazard 0.12 cells. The Bayesian observer outperformed the gate throughout the 12-cell grid.

## Interpretation and limitations

This is a bounded synthetic result: a state-conditioned gain can help a controller on tasks deliberately constructed so that observation reliability differs by motor mode, especially at lower target volatility. The same model loses at high volatility and remains below the task-informed Bayesian reference. Equal- and reversed-reliability post-result sensitivity tests further show that the advantage depends on the chosen mode/reliability relationship.

Ji et al. report locomotor-state-dependent AIY activity and a RIM-required corollary-discharge pathway; the paper does not establish that thermosensory measurement noise is higher during reversals. Thus the synthetic noise contrast is an assumption, not a biological finding. The implementation receives motor mode directly and does not model a RIM relay or learn that signal. This does not validate an AIY/RIM circuit equation, prove biological mechanism transfer, or establish a general AI inductive bias.

## Chronology and reproducibility

The no-gate control was changed from an arithmetic mean to a stationary-occupancy-weighted mean after initial output inspection. The corrected run is therefore post-result exploratory, not confirmatory. The superseded arithmetic-mean run is preserved separately and will be published as its own archived round. This package includes the correction note and contract to keep that chronology visible.

The episode CSV, condition summary, manifest and original result note are copied byte-for-byte from the corrected source run. The published runner changes only the output path to a timestamped directory. Historical dependency versions are not captured in this manifest.
