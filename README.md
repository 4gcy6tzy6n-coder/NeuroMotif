# NeuroMotif experiment archive

This repository preserves round-by-round model experiments, generated results, and lessons learned for the NeuroMotif project.

## Layout

- `model/<round>/` — runnable model or benchmark code.
- `data/results/<round>/` — generated result tables, machine-readable summaries, and verification records.
- `summery/<round>/` — protocols, scientific interpretation, strengths, failures, and corrections. The directory spelling follows the project owner's request.

Each experiment round is committed separately after its results and summary are reviewed. Results are retained as generated; later corrections and follow-ups use new versioned rounds or files.

## Evidence boundary

Synthetic benchmark outcomes are engineering results for their stated tasks. They are not biological validation or evidence of general AI benefit unless an experiment directly supports that claim. Consult each round's `summery/<round>/README.md` and `RESULTS.md` for scope and limitations.

## M2 route: published mechanism to synthetic computation

The active project route uses the published *C. elegans* AFD–AIY/RIM mechanism as a bounded biological reference and evaluates the project's synthetic abstractions. E4-v1 remains blocked by data-schema limitations; none of the M2 results below is biological validation. The complete run artifacts and round-specific caveats are in the linked `summery/<round>/RESULTS.md` files.

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

**Project-level reading:** these rounds do not establish that the published biological mechanism fails. They show that the current scalar feedback and state-gating implementations do not provide robust, general AI benefit in the tested synthetic settings. The defensible deliverable is a mechanism-transfer boundary analysis, not a claim of validated biological inductive bias. The current local NMI-readiness assessment is `NOT_READY`; see the route decision in the analysis workspace before making any venue claim.
## Additional completed synthetic studies

These are separate exploratory computations and do not belong to the M2 transfer portfolio. They are included to preserve the full evidence and correction history.

| Round | Result | Boundary |
|---|---|---|
| [M6 — State-gated inference](summery/M6_STATE_GATED_INFERENCE/README.md) | State-gated gain beat a single global gain descriptively but lost to a same-size innovation-adaptive filter in all primary hazard cells. | Two invalid metric attempts are retained and marked; only corrected v2 is authoritative. Synthetic only. |
| [M7 — Temporal-correlation boundary](summery/M7_TEMPORAL_CORRELATION_BOUNDARY/README.md) | Trace benefit varies with temporal correlation and delay; exact replay beat eligibility in all 48 tested cells. | The pooled accuracy/MSE interaction is invalid and excluded; objective-stratified analysis is authoritative. Synthetic only. |

The prospective biology route is currently deferred because access and assay capability have not been established. The published-worm-plus-synthetic route is a narrower reporting path, not completion of the original independent-validation objective.
