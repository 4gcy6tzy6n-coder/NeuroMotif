# M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1

**Status:** completed; `INCONCLUSIVE_TASK_VIABILITY_FAILED`. **Evidence class:** `ENGINEERING_ONLY | BOUNDARY`; outcome-informed at project level.

M12 tests whether an explicit motor-state-gated recurrent controller can imitate a known-generator Kalman observer/fixed-gain chase controller on a new closed-loop moving-target tracking task. Prior action determines sensory noise, and the controller is given the previous action as its motor-state input. The main comparison is against a parameter-matched generic GRU; zero-input and permuted-input controls test dependence on the motor-state path.

The study is grounded in the published *C. elegans* AFD–AIY/RIM motor-state feedback computation at cell-class scope. It does not use animal data, test biological validation, identify a unique synaptic carrier, or claim the synthetic task is homologous to worm thermotaxis. Prior M2 results are known; this is not confirmatory.

The frozen protocol is [`CONTRACT.md`](CONTRACT.md). Its SHA-256 is recorded in [`CONTRACT.sha256`](CONTRACT.sha256). Pre-run statistical and random-stream details are fixed in [`AMENDMENT_PRE_RUN_01.md`](AMENDMENT_PRE_RUN_01.md). The pre-run manifest is in `data/results/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/PREFLIGHT.json`.

**Execution:** all 40 paired seed blocks completed. The 7-unit gated model has 232 trainable parameters and the 6-unit GRU has 223 (4.04% difference, below the 5% limit). The prespecified benchmark-viability criterion failed: the known-generator reference improved over the reactive reference by 4.78%, below the 10% requirement. The run therefore remains inconclusive under the frozen contract. The pre-run verifier had a JSON serialization defect; its file and hash are preserved, and an independent corrective post-run checker passed all 27 checks.

**Next:** no v1 tuning. The project automatically returns to Route D, the evidence-boundary manuscript package. Full metrics, verifier issue, and interpretation limits are in [`RESULTS.md`](RESULTS.md).
