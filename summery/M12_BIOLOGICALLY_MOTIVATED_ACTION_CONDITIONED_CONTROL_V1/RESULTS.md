# M12 results — biologically motivated action-conditioned control

**Classification:** `ENGINEERING_ONLY | BOUNDARY`
**Frozen disposition:** `INCONCLUSIVE_TASK_VIABILITY_FAILED`
**Independent unit:** paired task-seed block (40 blocks; seeds 812000–812039)

## Execution and verification

The frozen run completed all 40 seed blocks, 128 test episodes per seed and arm, and 30 training epochs for each learned arm. Outputs contain 30,720 episode rows, 240 per-seed rows, and 4,800 training-log rows. The parameter-matched gated RNN and generic GRU had 232 and 223 parameters, respectively (4.04% difference; frozen limit 5%). The run used Python 3.12.13, NumPy 2.4.4, SciPy 1.17.1, PyTorch 2.11.0, macOS 26.2 arm64, and one Torch thread. Source and output hashes are recorded in `data/results/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/`.

The pre-run frozen verifier failed during report serialization because a NumPy boolean was not converted to a JSON-native boolean. The original verifier was preserved byte-for-byte. A separate post-run corrective checker was added; it verifies the original verifier's frozen hash and independently checks input/output hashes, row-key completeness, summary arithmetic, planned contrasts, task-viability calculation, and disposition. It passed all 27 checks. This is a disclosed reproducibility defect in the verifier, not a change to the contract, runner, generated outcomes, or statistical plan.

## Prespecified result

The first disposition gate failed. The known-generator reference improved normalized MSE over the reactive reference by **4.78%**, below the required **10%**; its failed-episode rate was 0%. Therefore the frozen outcome is `INCONCLUSIVE_TASK_VIABILITY_FAILED`, and the v1 task is not to be tuned or reinterpreted as a viable benchmark.

For transparency, the prespecified primary contrast was gated RNN minus generic GRU: **+0.002321 normalized MSE** (95% paired seed-bootstrap CI **[+0.001666, +0.003093]**); negative values would favor the gated model. The relative reduction was **−1.52%**, against the frozen +2% practical-benefit threshold. The gate failure makes this contrast descriptive for this nonviable generator; it does not establish a negative biological result or a general architecture disadvantage. The frozen secondary ablation contrasts did not support motor-path specificity (zero-input Holm-adjusted p=0.586; permuted-input Holm-adjusted p=0.170).

The automatic contract disposition controls interpretation despite these descriptive comparisons. M12 does **not** establish mechanism-specific transfer, biological validation, a unique RIM→AIY causal carrier, or failure of the published worm mechanism. It closes this exact synthetic implementation on this generator without authorizing a v1 tuning loop.

## Project consequence

The Route B test did not clear its prespecified viability gate. Under the owner-authorized automatic routing rule, the project returns to **Route D: an evidence-boundary manuscript package**. The reportable result is that this transfer test was inconclusive because the chosen benchmark did not satisfy its viability criterion, with the descriptive model contrasts retained as engineering evidence. This route switch does not retroactively change Fish1.5, E4-v1, M2, or any other historical result.

## Artifacts

- Frozen contract: [`CONTRACT.md`](CONTRACT.md)
- Pre-run amendment: [`AMENDMENT_PRE_RUN_01.md`](AMENDMENT_PRE_RUN_01.md)
- Runner: [`run_experiment.py`](../../model/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/run_experiment.py)
- Frozen verifier (serialization defect retained): [`verify_results.py`](../../model/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/verify_results.py)
- Corrective post-run checker: [`verify_results_postrun.py`](../../model/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/verify_results_postrun.py)
- Machine summary: [`SUMMARY.json`](../../data/results/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/SUMMARY.json)
- Verification: [`verification.json`](../../data/results/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/verification.json)
- Separate Feishu task-log entry: revision 88 of the project log, titled `M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1`.
