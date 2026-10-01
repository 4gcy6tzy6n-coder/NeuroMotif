# PROJECT_OWNER_AUTHORIZED_ROUTE_SWITCH_20261001

**Type:** project execution decision and evidence-matrix refresh. No biological outcomes or model outcomes were computed in this task.

## Decision

The owner authorization dated 2026-10-01 removes the old wait-for-owner route gate. Based on the repository's existing results, continue on **Route B: one published biological computation → a separately frozen, explicitly artificial transfer test**. Keep Route D as the automatic fallback if the new transfer test does not support its narrow prediction.

The selected biological reference remains *C. elegans* motor-state corollary discharge to AIY, at **cell-class level only**. The claim is now:

> Test whether an explicitly stated computational abstraction of published motor-state feedback can be useful in an artificial recurrent controller under fair controls.

Any positive model result will be called **biologically motivated AI transfer**. The project has not independently replicated the animal-level biological effect, identified a unique synaptic carrier, or validated a cross-species motif. The frozen worm E4-v1 remains schema-blocked and unrun.

## Why the prior route stopped

**Evidence:** no executable laboratory-access/assay plan is established; Fish1.5 is a one-specimen retrospective analysis whose positive recurrence–persistence association was not supported and whose frozen topology-null family was mostly undefined; worm E4-v1 cannot be reconstructed at the required animal level; R20-01 stops at projection-level public evidence. Existing M2 artificial controllers are mixed and include adverse parameter-matched comparisons. Other M4–M10 tasks concern different mechanisms and cannot be pooled.

**Inference:** Route A cannot currently be executed without a laboratory/data-access change. Route C does not have a shared, independently interpretable cross-system functional estimand in the current evidence. Route D is an honest fallback, but the owner's authorization makes a fresh, clearly separated Route B test the higher-information next scientific action.

The new Route B task must be a **new study**, not another tuning round in the closed M2 simulator. It must use an independent task family and a new architecture-level comparison, freeze model arms, parameter/training budgets, independent units, endpoints, multiplicity and stopping rules before generating outcomes, and include generic recurrent and mechanism-removal controls. Previous M2 outcomes make it post-result-informed at project level; the new package must say so and cannot be called a confirmatory replication.

## Evidence classification

The row-level inventory is in [`PROJECT_CURRENT_EVIDENCE_MATRIX_V2.csv`](PROJECT_CURRENT_EVIDENCE_MATRIX_V2.csv). Categories are claim-scoped: `POSITIVE` means only the named contrast or source finding; `NEGATIVE` means the declared positive prediction was not supported; `BOUNDARY` means evidence resolution/identifiability or generalization limit; `INVALID` means an inferential/measurement path cannot answer its frozen question; `ENGINEERING_ONLY` means synthetic/software evidence; `SUPPORTING` means context or candidate evidence that has not cleared the target claim. The CSV distinguishes the local authoritative record from its public mirror. The initial route update covered 35 rows; this post-M12 update adds one public round record, bringing the matrix to 36 rows. Other underlying source records remain outside this curated GitHub mirror. This archive-coverage limitation does not change their evidence status.

No effects across different tasks, animals, species, units or mechanisms are pooled. A source model reproducing a published result is not independent animal replication. A blocked test is not a biological negative. Projectome/projection resolution is not synapse-level identity.

## Route record

```text
WHY_PREVIOUS_ROUTE_STOPPED = NO_VERIFIED_LAB_ACCESS_OR_EXECUTABLE_PROSPECTIVE_ASSAY; EXISTING POSITIVE MOTIF-TO-AI CLAIM NOT ESTABLISHED
EVIDENCE_TRIGGER = OWNER AUTHORIZATION REMOVED WAIT-FOR-ROUTE-DECISION GATE; EXISTING M2 RESULTS LEAVE A DISTINCT ARCHITECTURE/TASK-FAMILY TRANSFER QUESTION OPEN
NEW_ROUTE = ROUTE_B; PUBLISHED C. ELEGANS MOTOR-STATE FEEDBACK -> NEW, INDEPENDENT-TASK ARTIFICIAL TRANSFER TEST
CLAIM_CHANGE = FROM NEWLY DISCOVERED/CROSS-SPECIES CONNECTOME MOTIF TO BIOLOGICALLY MOTIVATED COMPUTATIONAL TRANSFER; BIOLOGICAL VALIDATION REMAINS UNESTABLISHED
ROUTE_D_FALLBACK = IF THE FROZEN TRANSFER CRITERIA ARE NOT MET, COMPLETE THE EVIDENCE-BOUNDARY MANUSCRIPT PACKAGE WITHOUT ALTERING OLD RESULTS
```

## Source-integrity note

The local M5 evidence narrative cites Kimpo et al. (2014), DOI `10.7554/eLife.02076`, as an eyeblink-conditioning source. The DOI resolves to [*Gating of neural error signals during motor learning*](https://doi.org/10.7554/eLife.02076) and concerns vestibulo-ocular reflex learning, not the mouse delay-eyeblink result described in that narrative. The [2024 Silva et al. primary article](https://www.nature.com/articles/s41593-024-01594-7) directly supports the cited mouse delay-eyeblink claims, including CF stimulation as a substitute instructive signal and adaptation of response timing when the CS–US interval changed. This is a citation-scope correction only; it does not change any M5 artificial result. The M5 source narrative is now corrected in-place with an explicit amendment; see [`M5_PRIMARY_SOURCE_ATTRIBUTION_CORRECTION_01`](../M5_PRIMARY_SOURCE_ATTRIBUTION_CORRECTION_01/README.md). Frozen historical contracts remain unchanged.

## Immediate next execution

The Route B contract `M12_BIOLOGICALLY_MOTIVATED_ACTION_CONDITIONED_CONTROL_V1` is now frozen in the clean publication worktree. It specifies a new closed-loop tracking task, parameter-matched generic GRU, motor-input ablations, paired task-seed units, fixed training budget, viability criteria, and automatic disposition. The contract hash and pre-run state are recorded in its round package.

**Next execution (at route selection):** implement and run the frozen M12 study once; preserve every outcome; independently verify artifact completeness and summary arithmetic.

**Status (at route selection):** evidence inventory and route update complete; M12 contract frozen; implementation preflight passed; not run; no M12 outcome inspected. The post-run state is recorded below without changing this historical snapshot.

## Post-M12 automatic route update — 2026-10-01

M12 completed all 40 paired task-seed blocks. The known-generator reference's relative improvement over the reactive reference was 4.78%, below the contract's 10% task-viability threshold; therefore `M12 = INCONCLUSIVE_TASK_VIABILITY_FAILED`. A separate corrective checker passed all 27 verification checks after the frozen pre-run verifier failed to serialize a NumPy boolean. The frozen verifier, its hash, contract, runner, and outcomes remain unchanged; the verifier defect is documented in the M12 results. During manuscript integration, the broader local charter was checked and found to already mark Route D active and no nonredundant Route B question open before M12 execution. M12 is consequently supplemental, project-level outcome-informed engineering evidence, not a confirmatory Route B test; Route D remains active.

```text
WHY_PREVIOUS_ROUTE_STOPPED = ROUTE_B_M12 DID NOT CLEAR ITS FROZEN TASK-VIABILITY GATE; V1 MUST NOT BE TUNED
EVIDENCE_TRIGGER = 4.78% KNOWN-GENERATOR REFERENCE IMPROVEMENT < 10% PRESET THRESHOLD; CORRECTIVE POST-RUN VERIFICATION PASSED
NEW_ROUTE = ROUTE_D; COMPLETE THE EVIDENCE-BOUNDARY MANUSCRIPT PACKAGE
CLAIM_CHANGE = M12 IS AN INCONCLUSIVE ENGINEERING/BOUNDARY RESULT; IT DOES NOT SUPPORT OR FALSIFY THE PUBLISHED WORM MECHANISM OR A GENERAL AI BENEFIT
```

This route status records the post-M12 state in the public mirror; it is not a manuscript submission decision. Route A remains operationally unavailable without an executable lab/access path; Route C remains unqualified under the current evidence. The M12 row is added to the current evidence matrix, now 36 rows, as `BOUNDARY|ENGINEERING_ONLY`.

## Authoritative evidence files

- Owner execution authorization: local pasted attachment at `/Users/yyl/.codex/attachments/e5444d31-ad7d-4e87-af9d-b189388d9fd4/已粘贴的文本.txt` (not included in the public repository).
- [Whole-project reconciliation](../../experiments/biological_validation/PROJECT_FULL_SCOPE_RECONCILIATION_01.md)
- [M0–M10 portfolio evidence ledger](../PROJECT_CONVERGENCE_20261001/PROJECT_PORTFOLIO_EVIDENCE_LEDGER_V1.md)
- [Biological computation extraction](../../BIOLOGICAL_COMPUTATION_EXTRACTION.md)
- [Phase 2 observable matrix](../PHASE2_CROSS_SPECIES_MOTIF_FRAMEWORK_V1/PHASE2_EVIDENCE_TO_OBSERVABLE_MATRIX.md)
- [Route 2 transfer synthesis](../O3_ROUTE2_TRANSFER_SYNTHESIS_01/README.md)
- [Current venue-fit assessment](../PROJECT_FULL_SCOPE_VENUE_FIT_01/README.md)
- RR18/RR19 are separately owned; see [`RR18/README.md`](../../RR18/README.md).
