# Inputs and reproduction boundary

This post-result sensitivity analysis used only the pinned Fish1.5 primary 82-node cohort, its existing per-neuron metric table, the official crosswalk, and the Zenodo v1 `traced_axons_neurons.zip` archive. The runner calls the original graph builder at `scripts/run_fish15_experiment1.py`; it does not recompute calcium endpoints.

Required project-root inputs are enumerated with SHA-256 in `results/experiment1/postresult_recurrence_null_v1/PREFLIGHT.json`. The structural archive is the public Zenodo record [19231045 v1](https://zenodo.org/records/19231045), locally pinned as SHA-256 `b5aec9b38a23bce45bec0b1153ccc8b055671ce5b29b177e7aec185ff1a6077b`. The functional HDF5 hash is `386529a23a4943a1d125cb9592075e3c0b3d6239e68c60a1ae4cd2a9ec06f5db`.

The GitHub experiment archive stores the runner, contract, derived result tables, verification, and checksums; it does not mirror the large raw archive or the entire NMI analysis repository. Reproduction therefore requires restoring the listed public inputs at their recorded paths in the NMI project checkout. The simulation used the exact runner hash in `PREFLIGHT.json`; the post-run verifier separately checks saved null-rho summaries and reported invariants. Per-graph edge lists were not retained, and this limits independent graph-state auditing.
