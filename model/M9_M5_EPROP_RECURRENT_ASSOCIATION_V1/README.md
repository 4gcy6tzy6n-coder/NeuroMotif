# M9_M5_EPROP_RECURRENT_ASSOCIATION_V1

Post-result exploratory sequence-level delayed-association benchmark. This is an artificial learning-rule test, not biological validation.

`frozen_runner.py` is the exact hash-pinned local runner that generated the archived output. `run_m9.py` is the publication entry point; its only changes are routing the contract and output paths into this package.

From the NeuroMotif repository root, run `python3.12 model/M9_M5_EPROP_RECURRENT_ASSOCIATION_V1/run_m9.py`. It writes to `data/results/M9_M5_EPROP_RECURRENT_ASSOCIATION_V1/`. The input is fully synthetic. Python 3.12.13 and NumPy 2.4.4 were used.
