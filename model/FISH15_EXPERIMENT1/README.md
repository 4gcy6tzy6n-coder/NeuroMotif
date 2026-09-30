# FISH15_EXPERIMENT1 runner

This is the fixed retrospective runner for the single-specimen Fish1.5 structure–dynamics analysis. Run it from the NMI repository root after placing the public source files at the paths below. It writes its outputs under `results/experiment1/`.

```bash
python3.12 scripts/run_fish15_experiment1.py
```

Pinned input paths and SHA-256 digests are recorded in `data/results/FISH15_EXPERIMENT1/FISH15_EXPERIMENT1_PROVENANCE.json`. Required public inputs:

- `data/raw/fish15/clem_zfish1_functional_data.h5`
- `data/fish15/traced_axons_neurons.zip`
- `data/raw/fish15/source/Zebrafish_CLEM/1. Downloading_neuronal_morphologies_and_metadata/all_reconstructed_neurons.csv`
- `results/fish15/FISH15_C2_97_NEURON_STRUCTURAL_COVERAGE.csv`

The result package intentionally excludes the large raw archives. The current run was reproduced with Python 3.12.13, NumPy 2.4.4, SciPy 1.17.1, and h5py 3.16.0.
