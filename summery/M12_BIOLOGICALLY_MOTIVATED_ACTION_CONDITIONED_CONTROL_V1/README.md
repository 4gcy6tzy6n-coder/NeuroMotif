# M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1

**Status:** protocol frozen before implementation and outcome generation; not run. **Evidence class if run:** synthetic engineering transfer only; outcome-informed at project level.

M12 tests whether an explicit motor-state-gated recurrent controller can imitate a known-generator Kalman observer/fixed-gain chase controller on a new closed-loop moving-target tracking task. Prior action determines sensory noise, and the controller is given the previous action as its motor-state input. The main comparison is against a parameter-matched generic GRU; zero-input and permuted-input controls test dependence on the motor-state path.

The study is grounded in the published *C. elegans* AFD–AIY/RIM motor-state feedback computation at cell-class scope. It does not use animal data, test biological validation, identify a unique synaptic carrier, or claim the synthetic task is homologous to worm thermotaxis. Prior M2 results are known; this is not confirmatory.

The frozen protocol is [`CONTRACT.md`](CONTRACT.md). Its SHA-256 is recorded in [`CONTRACT.sha256`](CONTRACT.sha256). The pre-run manifest is in `data/results/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/PREFLIGHT.json`.

**Next:** implement the contract exactly, verify the parameter counts before training, then run once. No outcomes have been generated.
