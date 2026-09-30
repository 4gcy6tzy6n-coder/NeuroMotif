# M2_DAGGER_GRU_FOLLOWUP_V1

- Runner: `model/M2_DAGGER_GRU_FOLLOWUP_V1/run_closed_loop_dagger.py`
- Shared simulator/model dependency: `model/M2_DAGGER_GRU_FOLLOWUP_V1/run_closed_loop_experiment.py`
- Archived data and source result note: `data/results/M2_DAGGER_GRU_FOLLOWUP_V1/`
- Re-run from repository root with `python3 model/M2_DAGGER_GRU_FOLLOWUP_V1/run_closed_loop_dagger.py`.
- Reruns write to timestamped package-local folders. The DAgger runner and helper change only output routing; no training or evaluation was run for publication.
- This is a post-result baseline repair. It reuses the same already-inspected test environments and episodes as `M2_CLOSED_LOOP_V1`, so it is not independent confirmation.
- Synthetic only; the learned GRU is not capacity matched to the fixed controller. Historical Torch/NumPy versions are not recorded in this manifest.
