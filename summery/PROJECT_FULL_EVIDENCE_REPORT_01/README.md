# NeuroMotif full-project evidence report 01

**Date:** 2026-10-01  
**Status:** internal evidence-bounded synthesis; not a submission-ready manuscript.  
**Purpose:** give the whole project one auditable account after the original prospective-validation route could not be operationally confirmed. This is a synthesis of existing source-of-record documents, not a new experiment or pooled analysis.

## Executive decision

The original four-result positive chain is **not established**. The project has completed a whole-connectome test and a retrospective Fish1.5 analysis, but the Fish1.5 positive association was not supported and its frozen topology-null inference is invalid/indeterminate. Biological convergence across systems has not been established, and no validated biological mechanism has shown a motif-specific benefit in liquid/recurrent AI.

The project can responsibly report bounded results, mixed transfer attempts, and the reasons the original claim is currently unsupported. This supports an internal negative/boundary report. It does **not** by itself establish a novel general law about biological inspiration or meet current NMI readiness. The prospective validation route is deferred because access to a lab and assay capability have not been confirmed; this operational gap is not biological evidence.

```text
ORIGINAL_FOUR_RESULT_CHAIN = NOT_ESTABLISHED
M0_WHOLE_CONNECTOME = BOUNDED_NEGATIVE
FISH15_E1 = COMPLETE; POSITIVE_H1_NOT_SUPPORTED; FROZEN_NULL_INVALID/INDETERMINATE
CROSS_SYSTEM_CONVERGENCE = NOT_ESTABLISHED
BIOLOGICAL_MOTIF_TO_LNN_BENEFIT = NOT_ESTABLISHED
CURRENT_NMI_READINESS = NOT_READY
CURRENT_ROUTE = INTERNAL_PROJECT_WIDE_EVIDENCE_REPORT
PROSPECTIVE_BIOLOGY = DEFERRED; ACCESS/ASSAY UNCONFIRMED
```

## The four original claims

| Claim | Evidence and status | What the evidence permits |
|---|---|---|
| 1. Whole-connectome structure is sufficient for useful dynamics. | M0 did not show the proposed selective value-retention advantage over identity-like persistence under its frozen reservoir/interference assay. **Bounded negative.** | The tested topology and dynamics did not pass this assay. This does not show biological topology is generally useless. |
| 2. A local Fish1.5 recurrence motif predicts neural persistence. | Retrospective E1: 82 neurons, Spearman rho `−0.1096`, positive permutation `p=0.8337`, bootstrap 95% interval `[−0.2932, +0.1338]`; 861/1,000 frozen topology-null correlations undefined. The null preserves binary degrees and the global weight multiset, not node-specific weighted strengths. **Positive H1 not supported; combined disposition indeterminate because the frozen null is invalid.** | No positive recurrence→persistence association was established in this specimen. No population, causal, or cross-species conclusion follows. E1 remains complete as a frozen analysis, and its endpoint is not to be retuned. See the [task-compliance audit](../FISH15_E1_TASK_COMPLIANCE_AUDIT_01/README.md). |
| 3. The computation converges across biological systems. | Published Ji et al. worm evidence is cell-class-level prior literature; project E4-v1 animal-level reanalysis is blocked by missing auditable fields. Fish1.5 is non-supportive and one specimen; R20-01 is bounded by public substrate and projection-level resolution. **Convergence not established.** | Keep each system's source, resolution, and limitations separate. Literature evidence is not a project replication. |
| 4. A validated biological motif improves liquid/recurrent AI. | M2 tested worm-inspired state-feedback abstractions but outcomes were mixed/adverse against stronger controls; M4–M10 test distinct mechanisms/tasks. No candidate motif has passed the biological validation chain. **Transfer claim not established.** | Bounded algorithmic contrasts only. Do not pool unrelated tasks or present M5 eligibility traces as evidence for the worm mechanism. |

## What the wider portfolio adds

The M0–M10 ledger contains positive, negative, invalid, and inconclusive findings from different tasks, experimental units, model families, and levels of outcome-informed exploration. It does not have one common estimand, so a pooled effect or one-direction “portfolio result” would be misleading.

- **M2:** published worm work motivates a cell-class-level feedback abstraction. Existing controllers did not establish a robust mechanism-specific AI advantage; selected gates lose to generic adaptive controls, and optimization was inconclusive. The old tuning line is closed.
- **M4:** one Hopfield implementation underperforms exact MAP on its synthetic generator; the comparator is an optimal generator-specific ceiling and not resource matched.
- **M5/M7/M8/M9:** eligibility traces show task-bounded gains against no-trace in some conditions, while replay/BPTT are often stronger and benefits depend on task/delay. This is separate from the M2 worm mechanism.
- **M6:** the state gate can beat one fixed-gain baseline under stipulated informative context, but loses to generic adaptation and exact HMM in tested settings.
- **M10:** task viability failed across the delay grid; the trace contrast is inconclusive, not a learning-rule falsification.
- **Drosophila synthetic counterevidence:** demonstrates feature sufficiency under the constructed task, not a new biological result.
- **RR18/RR19:** separately governed lane; excluded from the M0–M10 synthesis except where the ledger explicitly identifies an adjacent boundary.

The detailed per-line evidence and source links remain in [`PROJECT_PORTFOLIO_EVIDENCE_LEDGER_V1.md`](../PROJECT_CONVERGENCE_20261001/PROJECT_PORTFOLIO_EVIDENCE_LEDGER_V1.md). The project-level contribution test is [`PROJECT_CONTRIBUTION_TEST_O2_V1.md`](../PROJECT_CONVERGENCE_20261001/PROJECT_CONTRIBUTION_TEST_O2_V1.md).

## Route change and rationale

The earlier recommendation to launch a prospective biological validation is superseded as the immediate route. No lab access or assay capability was established, so there is no confirmed prospective study that can be responsibly specified as ready to execute. This report therefore consolidates completed evidence and marks prospective biology as deferred. Do not treat lack of access as a negative biological result, and do not convert the published worm study into independent validation.

The existing Route 2 report is one bounded literature-grounded component, not a substitute for the original four-result chain. See [`full-scope reconciliation`](../../experiments/biological_validation/PROJECT_FULL_SCOPE_RECONCILIATION_01.md), [`Route 2 report V2`](../../experiments/biological_validation/O3_ROUTE2_RESEARCH_REPORT_DRAFT_V2.md), and [`Route 2 readiness decision`](../../experiments/biological_validation/O3_ROUTE2_NMI_READINESS_DECISION_01.md).

## Contribution and venue decision

Current evidence does not admit a positive motif-to-AI article. The negative/boundary synthesis is internally coherent as a project report, but its novelty and broad importance are not established; prior-work overlap and heterogeneous exploratory tasks limit an NMI Article or Analysis claim. **NMI readiness remains `NOT_READY`.** Any external manuscript route requires a separate contribution/venue decision and author review; this report is not a manuscript submission package.

## Reproducibility and release status

The experiment-package audit found all 26 local model and results package directories in the public repository, with matching package summaries. It compared 169 result artifacts (168 byte-identical; one repository index differs) and identified 26 Python copies with documented rerun-safe path/output adaptations. This closes coverage for those experiment packages only. Ancillary audit documents and full historical Feishu coverage remain partial; do not claim complete archival coverage. See [`archive coverage audit`](../PROJECT_EXPERIMENT_ARCHIVE_COVERAGE_01/README.md).

## Exact next action

Use this report for owner/author review and decide whether to pursue a narrower negative/boundary manuscript and which venue could support its actual contribution. Do not add another isolated simulation or claim prospective validation. Reopen prospective biology only when a specific accessible lab, assay, independent unit, and data path are confirmed; then design a new study before outcomes. This report does not complete the original four-result positive objective.

## Provenance

- Portfolio results: [`M0–M10 evidence ledger`](../PROJECT_CONVERGENCE_20261001/PROJECT_PORTFOLIO_EVIDENCE_LEDGER_V1.md)
- Original objective and completion status: [`full-scope reconciliation`](../../experiments/biological_validation/PROJECT_FULL_SCOPE_RECONCILIATION_01.md)
- Route replacement scope: [`Route 2 report V2`](../../experiments/biological_validation/O3_ROUTE2_RESEARCH_REPORT_DRAFT_V2.md)
- Contribution/venue readiness: [`O2 contribution test`](../PROJECT_CONVERGENCE_20261001/PROJECT_CONTRIBUTION_TEST_O2_V1.md)
- Experiment-package coverage: [`coverage audit`](../PROJECT_EXPERIMENT_ARCHIVE_COVERAGE_01/README.md)
