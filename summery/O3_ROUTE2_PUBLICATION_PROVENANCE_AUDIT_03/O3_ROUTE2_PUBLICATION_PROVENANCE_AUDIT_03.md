# O3 Route 2 — incremental M6/M7 release audit 03

**Date:** 2026-10-01  
**Scope:** Incremental publication of two completed exploratory synthetic rounds and a route-decision record. This does not claim that every historical project artifact has been released.

## Release findings

- M6 was committed separately as `c6958c66efab6e3a2c206aaa5612ed35b6856f7d`.
- M7 was committed separately as `ae543dae464eb84b3aacfb3211b9d3f314a41ed2`.
- The repository index amendment is `daf4363106ef0384870f959e4a2f043521b00f21`.
- The route switch after the unresolved feasibility condition is recorded as `0a9bd24e44a1224d009b331d22fc4c78b797dc38`.
- At verification, local publication HEAD and `neuromotif/main` both resolved to `0a9bd24e44a1224d009b331d22fc4c78b797dc38`; the working tree was clean.
- Required representative paths for M6, M7 and the route-decision summary were present in the remote tree. Package SHA-256 manifests validated locally, Python files passed AST syntax parsing, and archived outcome files matched their source records byte-for-byte. No experiment or outcome analysis was run for this release.

## Evidence boundaries

M6's corrected v2 metric is authoritative; invalid v0/v1 output directories and their invalidation records were retained. M7's objective-stratified analysis is authoritative; the pooled accuracy/MSE result remains explicitly invalid. Public runner/analyzer copies only change output routing to fresh directories. Both rounds are synthetic exploratory studies, not biological validation and not proof of general AI benefit.

## Coverage status

The 12 active-route M2 package audit remains valid for those 12 rounds. M6 and M7 are now separately published as additional exploratory studies. A directory-level comparison also found other local historical experiment and project-log folders absent from NeuroMotif; they have not been assumed to be active mainline rounds or automatically copied. Full historical M0–M10 and ancillary-artifact coverage therefore remains `PARTIAL` pending a deliberate scope/ownership classification, especially for separately governed RR18/RR19 material.

```text
M2_ROUTE_COVERAGE = COMPLETE (12/12 previously audited)
M6_PACKAGE = PUBLISHED_AND_VERIFIED
M7_PACKAGE = PUBLISHED_AND_VERIFIED
ROUTE_SWITCH_LOG = PUBLISHED
FULL_HISTORICAL_ARCHIVE_COVERAGE = PARTIAL
E4-v1 = BLOCKED_BY_DATA_SCHEMA (NOT RUN)
PROSPECTIVE_BIOLOGICAL_VALIDATION = DEFERRED
NMI_READINESS = NOT_READY (existing project assessment; not upgraded by publication)
```

## Next action

Continue with the evidence-bounded synthesis and deliberate classification of remaining historical artifacts before claiming whole-project archival completeness. Do not treat the M6/M7 upload as completion of the original biological-validation-to-LNN-transfer objective.
