# Fish1.5 figure contract

**Core conclusion:** The single-specimen analysis does not support the frozen positive association between local recurrence and post-offset persistence, while the frozen topology null is mostly undefined.

**Results-level question:** What does the frozen Experiment 1 show, and why can the graph-null comparison not adjudicate the combined gate?

**Figure archetype:** Quantitative two-panel evidence chain; separate single-panel descriptive robustness summary for Extended Data/Supplementary use.

**Target/output:** Nature Machine Intelligence exploratory draft; 177.8 mm main figure and 139.7 mm robustness figure (within the 180 mm production maximum), editable PDF/SVG and 600-dpi TIFF. Not a submission-ready figure or a claim that the current project meets NMI's evidence threshold.

**Backend:** Python/matplotlib, following the existing analysis workflow and saved figure preference.

## Panel map

- **a — Primary association:** all 82 strict-cohort neurons, exact recurrence-index x values (no jitter) versus post-offset persistence. Show Spearman rho, one-sided permutation p, endpoint n, and specimen count. No fitted line or confidence band is added.
- **b — Frozen topology-null estimability:** counts of 1,000 unique rewired graphs with defined versus undefined correlation statistic. State that the undefined statistic results from zero predictor variance; do not plot only the 139 defined graphs as if they represented the full null.
- **Extended robustness plot:** fixed robustness Spearman estimates only, without confidence intervals because none were specified for these secondary estimates. Label as descriptive and preserve the 82 versus 97 cohort n difference.

## Evidence hierarchy and reviewer risks

- Panel a is the primary evidence; panel b bounds the combined null-based decision.
- The 97-neuron and secondary endpoint correlations are demoted because they do not rescue the primary result.
- Replicate unit is neuron within one specimen (`N_specimen=1`); no animal-population inference.
- No outcome-derived exclusions or x jitter. All finite values are shown. No causal or circuit-carrier inference.
- The topology null preserves binary in/out degree and the global synapse-count weight multiset, but not each node's weighted strengths. Do not call it strength-preserving.
- Prior out-of-scope outcome exposure is disclosed; this is retrospective and partially informed.
- The combined experiment decision is indeterminate because 861/1,000 null statistics are undefined. The primary positive association test itself does not support H1.

## Source data and integrity

Use `FISH15_NEURON_METRICS.csv` and `FISH15_NULL_MODEL_RESULTS.csv`; include figure-panel source tables beside exports. No microscopy or image manipulation is involved. The source tables are derived from the pinned Fish1.5 HDF5 and Zenodo archive listed in `FISH15_EXPERIMENT1_PROVENANCE.json`.
