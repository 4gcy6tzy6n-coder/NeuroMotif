# M9_M5_EPROP_RECURRENT_ASSOCIATION_V2

Post-result exploratory sequence-level delayed-association benchmark. This is an artificial learning-rule test, not biological validation.

`frozen_runner.py` is the exact hash-pinned local runner that generated the archived output. `run_m9_v2.py` is the publication entry point: its only changes are repository paths for contract/output locations (and, for v2, correcting the contract filename that caused the disclosed post-run manifest-write failure).

From the NeuroMotif repository root, run `python3.12 model/M9_M5_EPROP_RECURRENT_ASSOCIATION_V2/run_m9_v2.py`. It writes to `data/results/M9_M5_EPROP_RECURRENT_ASSOCIATION_V2/`. The input is fully synthetic. Python 3.12.13 and NumPy 2.4.4 were used.
