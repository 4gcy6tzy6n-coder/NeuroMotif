# Closed-loop experiment: on-policy-trained GRU follow-up

**Status:** post-result baseline repair; exploratory. The same held-out simulator and exogenous test episodes as Experiment 3 were reused, so these results are not a new independent replication.

## Why this follow-up was run

The first GRU was trained on expert-action trajectories but evaluated on its own rollouts. That created a teacher-forcing distribution shift. I added Dataset Aggregation (DAgger): the current GRU generates closed-loop training states, the privileged proportional teacher labels those states, and the GRU is fine-tuned on the aggregated expert and on-policy data. This improves the learned baseline without changing the task or the fixed mechanism controller.

## Result

The updated GRU had lower mean absolute target error than the fixed gated controller in all 9 test cells. At target hazard `0.02` in the high-reversal-noise profile, DAgger-GRU error was `1.502`, versus `1.556` for the gate; the paired gate-minus-GRU difference was `+0.054` (95% episode-bootstrap interval `[+0.0463,+0.0615]`). The GRU also outperformed the occupancy-matched no-gate and memoryless scalar controllers in this cell (`1.502` versus `1.519` and `1.516`). The privileged teacher remained better (`1.471`).

The GRU contains 1,025 trainable parameters, compared with two principal fixed scalar coefficients in the handcrafted controller. This is not a capacity-matched comparison. Still, the result resolves the first baseline's most obvious training defect and removes any basis for treating the earlier GRU disadvantage as evidence favoring the biological abstraction.

## Training and reproducibility

- Code: [`run_closed_loop_dagger.py`](run_closed_loop_dagger.py).
- Test rows and paired comparisons: `closed_loop_dagger_experiment/episode_metrics.csv`, `condition_summary.json`.
- Training and seed record: `closed_loop_dagger_experiment/run_manifest.json`.
- Training used 512 expert trajectories followed by 3 DAgger rounds; each round added 512 current-policy trajectories and fine-tuned on the accumulated data.
- The final DAgger-round training MSE was `0.0057`; all 9 paired closed-loop test cells were already seen for the fixed controller and are explicitly not considered independent confirmation.

## Interpretation

The biologically inspired fixed gate did not outperform the trained recurrent control in closed-loop navigation. It also lost to simple scalar baselines on mean target error in the original Experiment 3. This is a negative result for the current fixed artificial implementation, not a falsification of the biological findings. Better transfer would require a computation that improves over a well-trained generic recurrent model under independent tasks and conditions, not a favorable comparison against a weakly trained baseline.
