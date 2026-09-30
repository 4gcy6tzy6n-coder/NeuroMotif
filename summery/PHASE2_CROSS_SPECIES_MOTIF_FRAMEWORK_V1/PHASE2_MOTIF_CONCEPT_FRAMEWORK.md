# Phase 2 — Cross-species structure–dynamics concept framework (v1)

**Purpose:** stop adding isolated experiments long enough to define a common concept vocabulary for the next project phase. This is a synthesis and planning artifact, not a new experiment, dataset analysis, or biological result.

## Mainline question

Which *computationally defined properties of neural circuits* can be operationalized across species without merging biological identities, and which have enough independent functional or intervention evidence to motivate a later transfer test?

The comparison unit is an abstract operation or property, not a neuron name, graph motif alone, or a pooled cross-species network. Biological modules remain separate. A shared term does not imply homologous cell types or equivalent biological mechanisms.

## Important category distinction

The proposed concepts do not all belong to one measurement layer. Convergence, divergence, routing depth, bottlenecks, and reciprocity are primarily **structural descriptors**. Feedback accessibility and multi-timescale recurrence are **dynamical/functional hypotheses** that require time-resolved activity and ideally intervention evidence. Structural graphs can indicate possible routes; they cannot alone establish signal flow, effective recurrence, memory, or causality.

Therefore Phase 2 must not collapse these concepts into one score or rank them by a single graph metric. For each concept, report separate evidence layers:

1. structural opportunity (anatomy/graph),
2. functional expression (activity/behavior over time),
3. causal contribution (intervention), and
4. artificial transfer (a separately frozen counterfactual).

## Candidate vocabulary (seven concepts)

| Concept | Portable operational definition | Structural observables | Functional/causal evidence needed | Main ambiguity to control |
|---|---|---|---|---|
| **Convergence** | Multiple distinguishable source populations provide input to a common target population or computation. | Source diversity, in-degree/weighted input concentration, source-class overlap. | Whether sources carry distinct information and jointly affect target response or behavior. | Degree alone ignores source identity, sign, state, and effective weight. |
| **Divergence** | One source population can influence multiple target populations or processing stages. | Out-degree, target-class diversity, distribution of paths from source. | Whether branches carry shared or differentiated signals and whether perturbing the source changes each target. | Anatomical fan-out is not functional broadcast. |
| **Routing depth** | Number and organization of intermediate transformations between a defined input and output. | Path-length distributions, layer/relay count, alternative paths under explicit edge rules. | Latency, transformation sequence, and input-to-output response under perturbation. | Shortest path is not necessarily the used path; edge thresholding can change depth. |
| **Bottleneck** | A node, edge, or small set whose removal disproportionately constrains access between specified source and target sets. | Cut sets, edge/node connectivity, flow or centrality measures with frozen weights. | Perturbation-induced loss, rerouting, compensation, and behavioral consequence. | High centrality is not causal necessity; redundancy and state dependence matter. |
| **Reciprocity** | Directed influence is present in both directions between specified units or populations. | Reciprocal edge fraction, dyad/motif counts, weighted directional balance. | Bidirectional influence on activity across time, ideally tested with directional intervention. | Reciprocal anatomy does not imply active feedback or a stable loop. |
| **Feedback accessibility** | A state/output-bearing population has a plausible route back to an earlier sensory/integration stage. | Reachability from defined output/state sets to input/integration sets; route classes and delays where known. | Time-ordered state-to-sensory modulation; perturbing the return route changes representation or behavior. | Must define “state/output” independently of the same graph being tested; path existence is only opportunity. |
| **Multi-timescale recurrence** | Recurrent interactions support distinguishable persistence or recovery timescales in a specified state/task. | Cycles and loop-length distributions as structural descriptors only. | Activity autocorrelation/decay, state transitions, perturbation recovery, and animal/session-level replication. | Cycle length is not a time constant; repeated frames/events are not independent animals. |

These definitions are candidates for a common glossary. They are not yet frozen analysis endpoints or a claim that every concept is measurable in every system.

## Current evidence modules: mapping without merging

| Existing module | Relevant candidate concepts | What is currently supported | What remains separate/unresolved |
|---|---|---|---|
| **M2 — C. elegans AFD–AIY/RIM** | Feedback accessibility; potentially reciprocity and persistence timescales | Published cell-class-level evidence links motor-state pathways requiring RIM to AIY sensory representation and sustained behavior under the tested thermotaxis conditions. | No exact L/R pairing, unique RIM→AIY causal carrier, or animal-level public Figure 6 linkage. Structural adjacency is not the intervention result. |
| **M3 — Fish1.5** | Convergence/divergence, routing depth, bottleneck, recurrence | Same-specimen functional↔EM crosswalk exists for explicit mapped IDs; acquired release provides structural/schema evidence. | Frozen switch-event/time alignment and choice/evidence observables are missing in the inspected functional release; current substrate does not identify the proposed computation. |
| **M4 — CA3 partial-cue recall** | Convergence, feedback/recurrence, bottleneck | Several paradigms support partial-cue retrieval involving CA3, while the necessity and exact recurrent carrier are disputed. | Recurrent collateral computation is not uniquely isolated; evidence cannot be reduced to “reciprocity” or a Hopfield identity. |
| **M5 — cerebellar instructive event** | Multi-timescale eligibility/persistence as an abstract temporal property | Timed climbing-fiber events causally instruct acquisition in a bounded conditioning task. | An eligibility trace/update equation remains an inferred abstraction; it is not the same claim as recurrent circuit memory. |
| **M0 — raw topology transfer baseline** | None as positive motif evidence | Historical topology-transfer results are negative within their tested settings and motivate changing the transfer unit. | Do not infer that any of these seven concepts is validated or that topology is universally useless. |

This mapping is a portfolio index, not a cross-species effect comparison. No biological node, trial, or result is pooled across rows.

## Selection rules before any new computation

A concept may advance from glossary to a computable candidate only after a **concept admission sheet** states:

- exact source and target sets and how they are defined independently of outcomes;
- the graph/data layer and provenance (anatomy, functional activity, behavior, perturbation);
- the required temporal and identity resolution, including the independent experimental unit;
- the estimand and what observation would falsify the claim;
- whether the measure is descriptive, functionally supported, or causally supported;
- null/control construction and known degeneracy risks;
- what cross-species comparison means without asserting biological equivalence;
- what data are missing and whether the concept is computable now.

Admission is blocked if a proposed metric depends on ambiguous node identity, unpinned graph materialization, outcome-informed thresholds, pseudoreplicated observations, or structural connectivity being treated as causal evidence.

## Proposed phase sequence

**Phase 2A — concept consolidation (this document):** agree on terms and keep structural descriptors separate from functional/dynamical claims. No new experiment.

**Phase 2B — evidence-to-observable matrix:** for each existing module, map each candidate concept to `DIRECTLY_OBSERVED`, `INTERVENTION_SUPPORTED`, `STRUCTURE_ONLY`, `SCHEMA_BLOCKED`, or `NOT_APPLICABLE`, with source citations and independent-unit/identity limits. This is evidence synthesis/schema mapping, not outcome reanalysis.

**Phase 2C — shortlist:** select at most two concepts for the next full analysis based on (i) clarity of biological identification, (ii) explicit computability, (iii) independent replication unit, (iv) cross-system interpretability, and (v) feasible counterfactual. Keep these axes separate; do not assign a blended “readiness score.”

**Phase 2D — new experiment only after shortlist:** freeze an estimand and controls first. Each experiment must serve the selected concept and a paper-level claim, not merely add another model/task result.

## Current decision

```text
NEW_EXPERIMENTS = PAUSED_DURING_PHASE2A/2B_SYNTHESIS
PHASE2_CONCEPT_SET = PROVISIONAL_SEVEN
STRUCTURAL_DESCRIPTORS != FUNCTIONAL_MECHANISM_EVIDENCE
CROSS_SPECIES_NEURON_MERGING = FORBIDDEN
NEXT_TASK = BUILD_EVIDENCE_TO_OBSERVABLE_MATRIX
NO_EXPERIMENT_OR_OUTCOME_ANALYSIS_AUTHORIZED_BY_THIS_DOCUMENT
```

This framework narrows the planning space; it does not choose the final two concepts or assert that any candidate is validated across species.
