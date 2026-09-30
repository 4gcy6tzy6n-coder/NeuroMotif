# Fish1.5 Experiment 1 task-compliance audit 01

**Date:** 2026-10-01  
**Type:** artifact/contract compliance review only. No traces or outcome tables were reanalysed; no statistic, effect, or p-value was recomputed.  
**Decision:** E1 is an existing completed analysis with explicit limits; the user-task specification was not fully met for the topology-null strength constraint. Preserve the frozen result and its `INDETERMINATE` combined disposition. This audit does not authorize a new null family or a rerun.

## Requirement-by-requirement status

| User-task requirement | Existing authoritative evidence | Audit status | Interpretation |
|---|---|---|---|
| Use exactly 82 strict complete neurons for primary; 15 incomplete IDs sensitivity-only | `results/experiment1/FISH15_EXPERIMENT1_CONTRACT.md`; `FISH15_NEURON_METRICS.csv`; `FISH15_EXPERIMENT1_VALIDATION_LOG.md` | **MET / artifact-verified** | The contract specifies the cohort and no size imputation. Validation records 82 primary nodes; metric output includes the sensitivity cohort. This is neuron-within-one-specimen analysis, not 82 animals. |
| Use four named HDF5 dot/sine arrays and code-defined nominal timing; do not claim embedded timing metadata | `FISH15_FUNCTIONAL_METRIC_DEFINITIONS.md`; `FISH15_EXPERIMENT1_PROVENANCE.json`; `FISH15_FUNCTIONAL_WINDOW_AUDIT.csv` | **MET WITH IDENTIFIABILITY LIMIT** | Timing is explicitly `OFFICIAL_ANALYSIS_CODE_DEFINED`, `dt=0.5 s`, nominal ON `[20,60) s`; it is not represented as HDF5 metadata or trial-level measured stimulus alignment. |
| Define six functional descriptors before analysis; persistence primary; preserve post-offset AUC sensitivity | `FISH15_FUNCTIONAL_METRIC_DEFINITIONS.md`; `FISH15_NEURON_METRICS.csv` | **MET WITH TWO UNAVAILABLE DESCRIPTORS** | Persistence, decay tau, onset rise, steady-state response and post-offset AUC are defined. Sine phase lag and calibrated gain are explicitly not identifiable from the released schema and are not computed. |
| Use explicit functional↔EM crosswalk, directed synapse-count weights, and no missing-size imputation | `FISH15_STRUCTURAL_METRIC_DEFINITIONS.md`; experiment provenance and edge audit referenced by the contract | **MET / contract-verified** | Primary graph counts validated synapse annotation records and does not use the incomplete size field. Graph identity is frozen to the explicit crosswalk. |
| Predefine structural descriptors and a single primary local-recurrence predictor | `FISH15_STRUCTURAL_METRIC_DEFINITIONS.md` | **MET / contract-verified** | Predictor is the normalized two-step return strength; other graph descriptors are secondary. |
| Test the frozen positive H1 with neuron-level Spearman association, permutation and bootstrap uncertainty | `FISH15_EXPERIMENT1_CONTRACT.md`; `FISH15_PRIMARY_RESULT.md`; `FISH15_PRIMARY_RESULT.json` | **MET / frozen result reported** | The source-of-record reports the primary association as not supporting the positive direction. These uncertainty procedures describe neuron-level variation conditional on one specimen and are not animal replication. This audit did not recompute them. |
| Build at least 1,000 directed topology nulls preserving node set, edge count, degree and weight distribution, and preferably node strengths | `FISH15_STRUCTURAL_METRIC_DEFINITIONS.md`; `FISH15_NULL_MODEL_RESULTS.csv`; `FISH15_EXPERIMENT1_VALIDATION_LOG.md` | **PARTIAL; INFERENCE INVALID/INDETERMINATE** | The frozen implementation generated 1,000 unique double-edge-swap graphs, preserving the node set, edge count and exact binary in/out degree sequence; it globally permuted the retained synapse-count weight multiset. It did **not** preserve node-specific weighted in/out strengths. Only 139/1,000 rewires yielded a defined correlation, so the frozen graph-null comparison is not estimable and has no reportable null p-value. The initial user-task wording called for a degree/strength-aware null; this is a real specification-to-contract gap. |
| Run fixed condition/cohort/persistence robustness analyses | `FISH15_ROBUSTNESS_RESULTS.md`; `FISH15_ROBUSTNESS_RESULTS.csv`; `FISH15_NEURON_METRICS.csv` | **ARTIFACTS PRESENT; SCOPE FIXED** | The frozen contract enumerates direction-specific dots, sine-identifiable outputs, 82/97 cohort and alternative AUC. This audit confirms records exist but does not recalculate or validate numerical values. |
| Apply no-imputation/no-response-based exclusions and log permitted missingness | `FISH15_FUNCTIONAL_METRIC_DEFINITIONS.md`; `FISH15_FUNCTIONAL_WINDOW_AUDIT.csv`; contract | **MET / contract and audit artifacts present** | Metric rules require complete windows and record undefined or single-direction cases; no interpolation or amplitude-based exclusions are specified. |
| Produce the named definition, contract, metric, primary, null, robustness and summary files | `results/experiment1/` | **PRESENT** | All eight required named artifacts are present. Supplemental provenance, audit, correction and figure-QA files also exist. Presence alone is not independent proof of every computation. |
| Stop after E1; no LNN/ANN training or new biological acquisition in this E1 task | `FISH15_EXPERIMENT1_CONTRACT.md`; current project records | **E1 STOP RULE HONORED** | E1 remains closed. The worktree contains separate project lines; they are not E1 execution. This audit does not open E3/E4/E5 or AI modeling. |

## Required claim boundary

The primary neuron-level association and the topology-null comparison have different statuses. The source record reports that the positive association is not supported; the frozen topology-null family is invalid/mostly undefined. The combined E1 result therefore remains `INDETERMINATE / INVALID FROZEN TOPOLOGY NULL`, not a positive result and not a general biological falsification.

The topology-null difference matters: preserving binary degree and the global weight histogram does not preserve node-level weighted strengths. Since the frozen contract and executed outputs are already outcome-exposed and specify the null family, this audit records the gap instead of replacing that family after seeing results. A future strength-preserving analysis, if ever separately authorized, would need a new version and transparent post-result status; it cannot retroactively repair E1-v1.

## Whole-project effect

This audit narrows the wording in the project synthesis: “E1 complete” means the frozen analysis and its primary association were executed and archived, while the required topology-null inference did not close. It must not be shortened to “the degree/strength-matched null passed.” The original four-result project objective remains incomplete: cross-system convergence and biological motif-to-LNN transfer are not established.

## Source records

- [Experiment 1 contract](../../results/experiment1/FISH15_EXPERIMENT1_CONTRACT.md)
- [Structural metric and null definitions](../../results/experiment1/FISH15_STRUCTURAL_METRIC_DEFINITIONS.md)
- [Functional metric definitions](../../results/experiment1/FISH15_FUNCTIONAL_METRIC_DEFINITIONS.md)
- [Primary result](../../results/experiment1/FISH15_PRIMARY_RESULT.md)
- [Null output](../../results/experiment1/FISH15_NULL_MODEL_RESULTS.csv)
- [Validation log](../../results/experiment1/FISH15_EXPERIMENT1_VALIDATION_LOG.md)
- [Full-scope reconciliation](../../experiments/biological_validation/PROJECT_FULL_SCOPE_RECONCILIATION_01.md)
