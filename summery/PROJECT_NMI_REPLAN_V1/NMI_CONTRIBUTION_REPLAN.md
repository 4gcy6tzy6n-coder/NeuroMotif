# NMI contribution replan after Phase 2 evidence synthesis

**Status:** internal project decision memo; not manuscript text and not an editorial prediction. It integrates the current project record through 2026-10-01 and official Nature Machine Intelligence content-type descriptions.

## 1. Evidence-locked position

The original positive arc was:

```text
local connectomic motif
→ reproducible temporal computation across systems
→ useful inductive bias in a liquid/recurrent network
```

The current record does not establish that chain:

- Phase-I whole-connectome selective-retention hypothesis was not supported under its frozen benchmark.
- Fish1.5 is one retrospectively analyzed specimen. Its fixed recurrence–post-offset-persistence association was negative (`rho = -0.1096`; one-sided `p = 0.8337`), so the predicted positive association was not supported. Its frozen graph-null comparison was invalid because 861/1,000 null statistics were undefined.
- The C. elegans E4 test is blocked by missing public temperature/stimulus alignment and auditable animal identity. Published cell-class evidence remains valid in its stated scope but is not a replication of the Fish1.5 estimand.
- R20-01 reaches projection-level evidence and cannot test a synapse-resolved motif.
- Existing M2 synthetic feedback tests do not show a robust transfer advantage over generic/adaptive controls. M5 eligibility-trace tests show bounded benefits over no-trace on synthetic objectives, but exact replay remains stronger and the tests do not implement a connectome-derived LNN bias. M10's XOR benchmark was not learnable across its delay grid.

**Therefore:** no shared biological motif is established, no motif is admitted to AI transfer, and the proposed four-result positive narrative must not be drafted as a demonstrated finding.

## 2. Current result that can be communicated accurately

> Across the tested project modules, neither whole-connectome topology nor the prespecified Fish1.5 local-recurrence measure established the proposed temporal-memory advantage. Complementary biological records differ in resolution and do not replicate one common estimand; current synthetic mechanism tests do not establish transfer from a validated connectomic motif.

This is a synthesis of bounded results, not proof that connectomes or biological motifs have no computational value.

## 3. Venue-fit assessment

Nature Machine Intelligence describes an **Article** as a substantial novel research study with a complex story, and an **Analysis** as a new analysis of existing data or comparative data leading to novel conclusions important to a broad audience. The current record does not yet demonstrate that level of novel general conclusion. This is consistent with the internal novelty/readiness audit, which found high overlap with the Fish1.5 source paper and established connectome-constrained/reservoir literature, while also documenting substantial limitations in independent biological replication and transfer.

Official guidance: [NMI content types](https://www.nature.com/natmachintell/content), [submission guidelines](https://www.nature.com/natmachintell/submission-guidelines).

Current route assessment:

| Route | Fit now | What is missing |
|---|---|---|
| Original positive NMI Article | **Not supported.** | A validated motif, independent biological evidence, a fair motif-specific artificial comparison, and independent task/environment generalization. |
| NMI Analysis based on current negative/inconclusive synthesis | **Not yet demonstrated.** | A novel, broad conclusion beyond a set of bounded negatives and evidence-resolution case studies; a precise contribution distinct from the source Fish1.5 paper and prior connectome-reservoir work. |
| Bounded negative/methodological report at a more suitable venue | **Potentially developable, not yet selected.** | Decide the contribution and venue; consolidate Phase-I methodological lessons with the Fish1.5 non-support/invalid-null result without overselling cross-system convergence. |
| Separate synthetic eligibility-trace paper | **A distinct possible project, not the current connectome-motif paper.** | Stronger fair baselines, task-family breadth, architecture-level testing, and a clear algorithmic contribution. It must not be presented as connectome-derived transfer. |

## 4. Recommended optimization of the project

Keep the intended NMI claim as a **long-term target**, but stop using the present analyses to imply it is nearly established. The most valuable next project work is a claim-and-contribution review, followed—only if retaining the NMI route—a new independent biological test of a narrowly defined computation and an independently evaluated artificial counterfactual.

A future biological study must specify one concept before outcomes, establish role/identity and independent units, and measure the relevant structure and temporal function at compatible resolution. It need not force every evidence layer into one dataset: triangulation is valid when each module answers a distinct claim and the manuscript does not pool them as replications. Existing blocked sources cannot be relabeled as positive evidence to satisfy this requirement.

Until such a study exists:

```text
NEW_FISH15_PREDICTOR_SEARCH = NOT_RECOMMENDED_ON_EXPOSED_ENDPOINT
C_ELEGANS_E4 = BLOCKED_BY_DATA_SCHEMA
R20_01 = PROJECTION_LEVEL_BOUNDARY_ONLY
AI_TRANSFER_FROM_VALIDATED_MOTIF = NOT_ELIGIBLE
NMI_POSITIVE_ARTICLE_DRAFT = NOT_READY
NEXT_WORK_PACKAGE = AUTHOR_REVIEW_OF_CONTRIBUTION_AND_VENUE
```

This is not a request to resume broad dataset hunting or to run another isolated model task. It is the decision point between (a) investing in a genuinely independent biological test to preserve the original NMI objective, and (b) writing a bounded negative/methodological report with a more appropriate contribution and venue.

## 5. Required human decision after review

The project team must choose which outcome is the actual paper objective:

1. **Preserve the positive NMI transfer claim** and commit to obtaining/producing independent biological evidence plus a new prospective transfer study; or
2. **Reframe around the current bounded negative/inconclusive evidence** and evaluate a more suitable journal and novelty claim.

No experiment or model run is authorized by this memo. It prepares a concrete decision from the completed evidence; it does not freeze a new biological estimand.

## Source-of-record files

- `results/experiment1/PROJECT_ROADMAP.md`
- `results/experiment1/NMI_PROJECT_CLAIM_EVIDENCE_LEDGER.md`
- `results/experiment1/NMI_MANUSCRIPT_ARGUMENT_AND_READINESS.md`
- `results/experiment1/NMI_NOVELTY_PRECEDENT_AUDIT.md`
- `summery/PHASE2_CROSS_SPECIES_MOTIF_FRAMEWORK_V1/PHASE2_EVIDENCE_TO_OBSERVABLE_MATRIX.md`
- `summery/M8_TRACE_HORIZON_FRONTIER/RESULTS.md`
- `summery/M9_M5_EPROP_RECURRENT_ASSOCIATION_V2/RESULTS.md`
- `summery/M10_M5_EPROP_TEMPORAL_XOR_V1/README.md`
