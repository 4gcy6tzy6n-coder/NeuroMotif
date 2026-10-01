# M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1

**Status:** protocol frozen; implementation preflight passed; outcome generation not started. **Evidence class if run:** synthetic engineering transfer only; outcome-informed at project level.

M12 tests whether an explicit motor-state-gated recurrent controller can imitate a known-generator Kalman observer/fixed-gain chase controller on a new closed-loop moving-target tracking task. Prior action determines sensory noise, and the controller is given the previous action as its motor-state input. The main comparison is against a parameter-matched generic GRU; zero-input and permuted-input controls test dependence on the motor-state path.

The study is grounded in the published *C. elegans* AFD–AIY/RIM motor-state feedback computation at cell-class scope. It does not use animal data, test biological validation, identify a unique synaptic carrier, or claim the synthetic task is homologous to worm thermotaxis. Prior M2 results are known; this is not confirmatory.

The frozen protocol is [`CONTRACT.md`](CONTRACT.md). Its SHA-256 is recorded in [`CONTRACT.sha256`](CONTRACT.sha256). Pre-run statistical and random-stream details are fixed in [`AMENDMENT_PRE_RUN_01.md`](AMENDMENT_PRE_RUN_01.md). The pre-run manifest is in `data/results/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/PREFLIGHT.json`.

**Pre-run check:** the 7-unit gated model has 232 trainable parameters and the 6-unit GRU has 223 (4.04% difference, below the 5% limit). Contract, amendment, source-code, and resolved-config hashes match the frozen preflight record. No performance outcomes have been generated.

**Next:** execute the frozen run once; keep all arms, seeds, episodes, and failure outputs.
