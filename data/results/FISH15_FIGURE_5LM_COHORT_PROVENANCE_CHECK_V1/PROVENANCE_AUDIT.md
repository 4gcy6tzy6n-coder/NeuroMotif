# Fish1.5 Figure 5l,m cohort provenance audit

**Task code:** `FISH15_FIGURE_5LM_COHORT_PROVENANCE_CHECK_V1`  
**Date:** 2026-09-30  
**Status:** `PUBLIC_RECORDS_VERIFIED / COHORT_RELATION_UNRESOLVED`  
**Scope:** Public provenance and figure/sample metadata only. No archive download, trace inspection, or outcome analysis.

## Question

Does the author-deposited Zenodo dataset for Figure 5l,m document the same cohort as, a separate cohort from, or a replacement for the seven-fish Figure 5g–i validation described in the v2 preprint?

## Evidence checked

1. The [official Zenodo record 19598932](https://zenodo.org/records/19598932), published 2026-04-15, is titled “Imaging data for Figure 5l,m in Boulanger-Weill et al. (2026).” Its README says it contains processed imaging from six larval zebrafish, four imaging planes per fish, stimulus timing/identity, HDF5 traces, and cell-type labels. The record's related-work metadata links it as a supplement to preprint DOI [10.1101/2025.03.14.643363](https://doi.org/10.1101/2025.03.14.643363). Raw data are available upon request. The processed archive is 2.8 GB and was not downloaded.
2. The [PMC-hosted v2 preprint](https://pmc.ncbi.nlm.nih.gov/articles/PMC11952533/) labels its model validation in Fig. 5g–i and states “n=7 fish, 2 planes per fish, and 12 trials per plane.” The full text is also available from the [Europe PMC full-text endpoint](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11952533/fullTextXML).

## Finding

The public sources verify two distinct metadata descriptions: a six-fish/four-plane Figure 5l,m dataset deposited in 2026, and a seven-fish/two-plane Figure 5g–i experiment in the inspected v2 preprint. Their figure-panel labels and sample/plane counts differ. The Zenodo record's relation to the preprint establishes manuscript-level association, but does not state whether the Figure 5l,m observations are an independent cohort, an expanded/reprocessed version, or a later replacement/extension of the Figure 5g–i experiment.

Therefore:

```text
FIG5LM_RECORD_PUBLIC = VERIFIED
FIG5LM_SAMPLE_DESCRIPTION = 6_FISH × 4_PLANES
V2_FIG5G_I_SAMPLE_DESCRIPTION = 7_FISH × 2_PLANES
COHORT_RELATION = UNRESOLVED_FROM_PUBLIC_METADATA
SAME_COHORT = NOT_ESTABLISHED
INDEPENDENT_COHORT = NOT_ESTABLISHED
POOLING_OR_REPLACEMENT = NOT_JUSTIFIED
```

The appropriate interpretation is unresolved provenance, not proof that the cohorts are different or that the records conflict. A direct author clarification or an authoritative versioned methods/data statement that explicitly maps panels to acquisition sessions would be needed to close this question.

## Project consequence

The Figure 5l,m record cannot currently be used as independent replication of the v2 Figure 5g–i cohort, or as an extension of Fish1.5 Experiment 1's frozen 82-neuron structure–function estimand. Its README does not document the EM identity crosswalk needed for that estimand. This provenance check changes no existing Fish1.5 Experiment 1 result and does not authorize downloading or analyzing the 2.8 GB archive.

## Reproducibility

This audit records the official record and preprint metadata used, the unresolved join between them, and a bounded closure criterion. No biological outcome was inspected or calculated.
