# M9-v2 execution incident and resolution

The frozen runner completed training, generated the full 270-cell result table, computed the JSON summaries, and wrote the Markdown report. It then exited with `FileNotFoundError` while creating its final run manifest because the copied runner still referenced `M9_CONTRACT.md` instead of this version's `M9V2_CONTRACT.md`.

The failure occurred after outcome generation and did not alter metric files. The runner and contract still match the pre-run SHA-256 values in `M9V2_PREFLIGHT.json`. We retained the frozen runner unchanged and used the separate `verify_m9_v2.py` to independently recompute seed-level contrasts, bootstrap intervals, the BPTT viability gate, row completeness, and file hashes from the saved outputs. It writes a recovered manifest and post-run verification record; it does not retrain or change outcomes. The run is reported with this operational defect disclosed.
