# NeuroMotif experiment archive

This repository preserves round-by-round model experiments, generated results, and lessons learned for the NeuroMotif project.

## Layout

- `model/<round>/` — runnable model or benchmark code.
- `data/results/<round>/` — generated result tables, machine-readable summaries, and verification records.
- `summery/<round>/` — protocols, scientific interpretation, strengths, failures, and corrections. The directory spelling follows the project owner's request.

Each experiment round is committed separately after its results and summary are reviewed. Results are retained as generated; later corrections and follow-ups use new versioned rounds or files.

## Evidence boundary

Synthetic benchmark outcomes are engineering results for their stated tasks. They are not biological validation or evidence of general AI benefit unless an experiment directly supports that claim. Consult each round's `summery/<round>/README.md` and `RESULTS.md` for scope and limitations.

## Current owner-authorized route: new Route B transfer study

The owner authorized continued scientific execution without waiting for a venue or story choice. The current route is a new, separately frozen artificial transfer test grounded in the published *C. elegans* AFD–AIY/RIM motor-state feedback mechanism, at cell-class scope. Existing M2 experiments remain historical and closed to retuning; the new study must use a distinct task family and architecture-level comparison. E4-v1 remains blocked by public data schema and has not been run. Any model result can support only a **biologically motivated AI transfer** claim, not biological validation. If the frozen test does not support its bounded prediction, the project will route to an evidence-boundary manuscript. See the [owner-authorized route decision and current evidence matrix](summery/PROJECT_OWNER_AUTHORIZED_ROUTE_SWITCH_20261001/README.md).

The new Route B transfer contract is frozen as [M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1](summery/M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1/README.md); it has not yet been implemented or run.

The archived M2 runs below are the completed historical transfer attempts; their results are not pooled or changed by the new route decision. The complete run artifacts and round-specific caveats are in the linked `summery/<round>/RESULTS.md` files.

| Round | What the archived result supports | Boundary / disposition |
|---|---|---|
| [Action-feedback pilot](summery/M2_ACTION_FEEDBACK_PILOT_V1/README.md) | Previous-action feedback can help relative to a memoryless threshold in some noisy conditions. | Exploratory scalar abstraction; a task-informed Bayesian observer was stronger. |
| [Boundary extension](summery/M2_PILOT_BOUNDARY_EXTENSION_V1/README.md) | A fixed feedback value can become harmful as target volatility rises. | Post-pilot exploratory; maps a synthetic failure regime. |
| [Bayesian benchmark](summery/M2_PILOT_BAYESIAN_BENCHMARK_V1/README.md) | An exact observer given generator parameters beat the simple controllers in the initial grid. | Task-specific oracle, not a capacity-matched learned model. |
| [Bayesian follow-up](summery/M2_BAYES_FOLLOWUP_V1/README.md) | The oracle advantage persisted across nine synthetic environments at 1,000 episodes each. | Post-result follow-up; known-generator setting, not general AI evidence. |
| [State-gate V0 archive](summery/M2_STATE_GATED_GAIN_V0_ARCHIVE/README.md) | Preserves the initial no-gate control error. | Superseded; the original runner was not preserved, so exact rerun is unavailable. |
| [State-gated gain V1](summery/M2_STATE_GATED_GAIN_V1/README.md) | A corrected gate outperformed a parameter-count-matched additive control in 9 of 12 cells, but lost in the three high-volatility cells. | Post-result correction; advantage depended on an unverified synthetic mode/reliability relationship; Bayesian observer remained stronger. |
| [Reliability-shift V0 archive](summery/M2_RELIABILITY_SHIFT_V0_ARCHIVE/README.md) | Preserves the initial sensitivity-control error. | Superseded; original runner was not preserved. |
| [Reliability-shift V1](summery/M2_RELIABILITY_SHIFT_V1/README.md) | Fixed gate advantage did not hold when the mode/reliability relation was removed or reversed. | Post-result sensitivity only. |
| [Closed-loop control](summery/M2_CLOSED_LOOP_V1/README.md) | The fixed gate had higher target error than simple controls in all nine tested cells. | Synthetic controller failure boundary; not a biological failure. |
| [DAgger follow-up](summery/M2_DAGGER_GRU_FOLLOWUP_V1/README.md) | The repaired GRU beat the fixed gate in all nine cells. | Post-result baseline repair on reused test episodes; not independent confirmation or capacity matching. |
| [Parameter-matched hazard test](summery/M2_PARAMETER_MATCHED_HAZARD_V1/README.md) | Corrected crossed-bootstrap interval favored the learned no-gate controller on the tested grid. | Outcome-informed synthetic follow-up; hazard holdouts do not constitute a new task family. |
| [Targeted-gain optimization](summery/M2_TARGETED_GAIN_OPTIMIZATION/README.md) | The primary learned-gain comparison was inconclusive, with opposite signs across the two hazards. | Optimization line stopped; no further tuning is justified by this result. |

**Project-level reading:** these rounds do not establish that the published biological mechanism fails. They show that the tested scalar feedback and state-gating implementations did not provide robust, general AI benefit in the tested synthetic settings. They do not close the new, distinct Route B study. No synthetic result is biological validation, and the local NMI-readiness assessment remains `NOT_READY`.
## Additional completed synthetic studies

These are separate exploratory computations and do not belong to the M2 transfer portfolio. They are included to preserve the full evidence and correction history.

| Round | Result | Boundary |
|---|---|---|
| [M6 — State-gated inference](summery/M6_STATE_GATED_INFERENCE/README.md) | State-gated gain beat a single global gain descriptively but lost to a same-size innovation-adaptive filter in all primary hazard cells. | Two invalid metric attempts are retained and marked; only corrected v2 is authoritative. Synthetic only. |
| [M7 — Temporal-correlation boundary](summery/M7_TEMPORAL_CORRELATION_BOUNDARY/README.md) | Trace benefit varies with temporal correlation and delay; exact replay beat eligibility in all 48 tested cells. | The pooled accuracy/MSE interaction is invalid and excluded; objective-stratified analysis is authoritative. Synthetic only. |

The prospective biology route is currently deferred because access and assay capability have not been established. The published-worm-plus-synthetic route is a narrower reporting path, not completion of the original independent-validation objective.

## Other archived completed rounds

These rounds are preserved separately from the 12-round M2 route portfolio above. Several are post-result follow-ups, controls, or mechanism-specific simulations; do not count them as independent biological replications or pool them into one effect. Each package retains its own contract, outcomes, and failure/correction history.

| Round | Evidence category and boundary |
|---|---|
| [Forward-state sensory gate V1](summery/M2_FORWARD_STATE_SENSORY_GATE_V1/README.md) | Initial synthetic transfer; exploratory and conditional on a designed state–noise mapping. |
| [Forward-state sensory gate V2](summery/M2_FORWARD_STATE_SENSORY_GATE_V2/README.md) | Follow-up implementation; same synthetic mechanism family, not independent confirmation. |
| [Forward-state sensory gate V3](summery/M2_FORWARD_STATE_SENSORY_GATE_V3/README.md) | Broader synthetic hazard/control comparison; does not validate the biological mechanism. |
| [Feedback-site specificity V3](summery/M2_FEEDBACK_SITE_SPECIFICITY_V3/README.md) | Post-result source-model simulation; motor-only control did not fully match the sensory-feedback dynamics. |
| [Feedback-site specificity V4](summery/M2_FEEDBACK_SITE_SPECIFICITY_V4/README.md) | Post-result stress test with stronger duration matching; remains a model-specific counterfactual. |
| [Cross-task state feedback V1](summery/M2_CROSS_TASK_STATE_FEEDBACK_V1/README.md) | Synthetic cross-task controller study; task and output limits are in its round report. |
| [Closed-loop active sensing V1](summery/M2_CLOSED_LOOP_ACTIVE_SENSING_V1/README.md) | Exploratory closed-loop synthetic study; comparator and information-deadlock caveats are retained. |
| [Forward-state decision transfer V1](summery/M2_FORWARD_STATE_DECISION_TRANSFER_V1/README.md) | Outcome-informed readout follow-up using the V3 model; not an independent model-training replication. |
| [Ji 2021 feedback dynamics](summery/M2_JI2021_FEEDBACK_DYNAMICS/README.md) | Reimplementation/simulation of a published source model; not new animal data. |
| [Ji 2021 feedback-site control V1](summery/M2_JI2021_FEEDBACK_SITE_CONTROL_V1/README.md) | Post-result model counterfactual with imperfect run-duration matching. |
| [Ji 2021 feedback-site control V2](summery/M2_JI2021_FEEDBACK_SITE_CONTROL_V2/README.md) | Follow-up with finer duration calibration; source-model evidence only. |
| [RIM-ablation Figure 6C reanalysis](summery/M2_RIM_ABLATION_SOURCE_REANALYSIS/README.md) | Descriptive event-level reanalysis; the public table does not identify animal/session, so no animal-level inference. |
| [Eligibility trace temporal XOR V2](summery/M5_ELIGIBILITY_TEMPORAL_XOR_V2/README.md) | Post-result synthetic optimizer/task follow-up; eligibility remained below BPTT. |
| [Drosophila counterevidence robustness V1](summery/DROSOPHILA_COUNTEREVIDENCE_ROBUSTNESS_V1/README.md) | Synthetic reduced-order transfer/counterevidence study, not fly data. |
| [Drosophila natural-scene counterevidence V1](summery/DROSOPHILA_COUNTEREVIDENCE_NATURAL_SCENE_V1/README.md) | Exploratory rendered-image benchmark using CC0 panorama previews; not biological data or a general vision benchmark. |

The local-to-public package audit covers all 26 top-level local `model/` and `data/results/` round folders. Some source inputs are intentionally not bundled: the natural-scene acquisition package includes its public source manifest and downloader, while the published-paper workbook/source archive used by other rounds must be retrieved from the cited source record.

## Project archive coverage

The audit at [`summery/PROJECT_EXPERIMENT_ARCHIVE_COVERAGE_01/README.md`](summery/PROJECT_EXPERIMENT_ARCHIVE_COVERAGE_01/README.md) verifies that all 26 local model/result package directories and their per-round summaries are represented in this repository. It includes a per-file SHA-256 manifest and records the rerun-safe source-path adaptations. This closes the experiment-package coverage audit only; ancillary project documents and separately governed RR18/RR19 records are outside its scope. Scientific result states and NMI readiness are unchanged.

## Whole-project evidence status

The original four-result positive chain is not established: the tested whole-connectome result is a bounded negative; Fish1.5 E1 did not support its positive recurrence–persistence hypothesis and its frozen topology null is invalid/indeterminate; cross-system convergence and biological motif-to-LNN benefit remain unestablished. The prospective biology route is deferred because laboratory access and assay capability are unconfirmed. This is an operational limit, not a biological negative result. See the [full-project evidence report](summery/PROJECT_FULL_EVIDENCE_REPORT_01/README.md), [Fish1.5 task-compliance audit](summery/FISH15_E1_TASK_COMPLIANCE_AUDIT_01/README.md), and [venue-fit decision](summery/PROJECT_FULL_SCOPE_VENUE_FIT_01/README.md). These are internal evidence-bounded records, not a submission-ready manuscript; NMI readiness remains not ready.
