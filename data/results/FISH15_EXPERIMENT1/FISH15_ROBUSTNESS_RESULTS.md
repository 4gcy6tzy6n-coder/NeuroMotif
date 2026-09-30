# Fish1.5 Experiment 1 fixed robustness results

These checks were enumerated in the retrospective analysis contract. An earlier out-of-scope calculation exposed outcomes, so this report is partially informed and is not a prospective preregistration or confirmatory analysis. The checks are descriptive and cannot replace the primary endpoint. The dataset is one specimen; no result generalizes to the zebrafish population.

| Fixed analysis | n | Spearman rho | Status |
|---|---:|---:|---|
| left_dots | 82 | -0.1334 | COMPUTED |
| right_dots | 82 | 0.0397 | COMPUTED |
| post_offset_auc_60_70 | 82 | -0.0344 | COMPUTED |
| onset_rise_time_10_90 | 82 | 0.0383 | COMPUTED |
| decay_tau_60_80 | 82 | 0.0045 | COMPUTED |
| sine_steady_response | 82 | 0.1430 | COMPUTED |
| expanded_97_node_sensitivity | 97 | -0.1031 | COMPUTED |

Sine phase lag and calibrated gain are not identifiable from the released schema. The 97-neuron sensitivity cohort uses the induced expanded graph; it does not upgrade the unit of inference. No robustness result changes the primary decision.
