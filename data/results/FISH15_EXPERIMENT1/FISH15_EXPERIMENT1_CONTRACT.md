# Fish1.5 Experiment 1 contract

**Candidate:** Fish1.5-C2-H1, unsigned local recurrence ↔ nominal post-offset persistence.  
**Status:** `RETROSPECTIVELY_SPECIFIED / SINGLE_SPECIMEN / NOT_CONFIRMATORY`.  
**No outcome values have been inspected or computed under this Experiment 1 contract as of this freeze.** Prior array-shape/missingness, mapping, edge-join, published dynamics/model claims and archive schema are known and listed in `FISH15_C2_PRIOR_KNOWLEDGE_LEDGER.md`.

## Question and hypothesis

Within the single Fish1.5 specimen, is greater `LOCAL_RECURRENCE_INDEX` associated with greater `POST_OFFSET_PERSISTENCE` across the fixed 82-neuron primary cohort?

```text
H1 direction: positive association
Unit: neuron within this one specimen
Scope: specimen-conditional association only
```

An association does not establish causal synaptic transmission or a zebrafish population effect. The claim will not be generalized to fish populations, and neurons/trials/frames/null graphs/bootstraps will not be called independent animals.

## Frozen cohorts and primary analysis

- Primary cohort: exactly 82 strict structural-complete functional IDs from the existing schema audit.
- Sensitivity-only structural cohort: the other 15 explicit mapped IDs, processed with the same rules and no filling of missing size fields. The primary topology metric does not use size.
- Primary endpoint and predictor are frozen in the paired metric-definition files.
- Primary statistic: Spearman rho between `LOCAL_RECURRENCE_INDEX` and `POST_OFFSET_PERSISTENCE`, using all primary neurons with a defined persistence endpoint. Report actual n and single-direction/missing-endpoint counts.
- Directional primary test: positive-rho label permutation test with 10,000 permutations of persistence values across the fixed eligible primary neurons; use `(1 + # permuted rho >= observed rho)/(1+10000)`. Report also the two-sided descriptive permutation tail. This exchangeability assumption is limited to a within-specimen neuron-label null and is not animal-level inference.
- Uncertainty: 10,000 paired neuron bootstrap resamples for a 95% percentile interval of rho, conditional on this specimen. This interval is descriptive and does not account for animal-to-animal variation or all network dependence.
- Primary topology counterfactual: 1,000 degree-preserving, globally weight-matched directed graph rewires, as specified in `FISH15_STRUCTURAL_METRIC_DEFINITIONS.md`. Compare observed rho with the null rho distribution; empirical upper-tail fraction is `(1 + # null rho >= observed rho)/(1+1000)`. The null is not per-node strength-preserving.
- Exactly one primary predictor/endpoint/test pair. No endpoint or predictor may be promoted based on results.

## Secondary and fixed robustness analyses

Secondary descriptors: in/out strength, reciprocal strength/fraction, two-step return strength, and three-step return strength against the primary endpoint. Report all; do not select one. Apply Holm adjustment across this prespecified family of secondary association tests.

Fixed robustness outputs: left dots only; right dots only; sine arrays only for metrics that are identifiable (steady response only, no phase lag/gain); alternative post-offset AUC; onset rise time; decay tau; 82-node versus 97-node sensitivity cohort. Each uses the same stated metric and identity rules. No robustness result replaces the primary outcome.

## Missingness, provenance and source-view rules

- No imputation.
- A trial is usable only when all samples in the windows required for that metric are finite. A neuron with no usable trial metric for either direction has missing primary endpoint and is reported with its fixed reason; no response-size or direction-preference exclusion is permitted.
- Persistence ratio with exactly zero/nonfinite final-stimulus denominator is undefined for that trial; omit that trial metric, record count, and do not impose an amplitude threshold.
- Timebase stays `OFFICIAL_ANALYSIS_CODE_DEFINED`, nominal `dt=0.5 s`, nominal stimulus `[20,60) s`; no HDF5-embedded time metadata is claimed.
- Structural topology uses the frozen archive/crosswalk rule only. Presynaptic owner table determines W; postsynaptic files serve as a frozen identity/integrity cross-check, not as an alternate source to fill absent primary edges.
- Sine phase lag and calibrated sine gain are not identifiable from released schema and will be reported unavailable.

## Interpretation rules

- Positive primary association plus topology-null separation: report only a retrospective within-this-specimen association, conditional on the pinned data and nominal code timing.
- Primary association not above the frozen criterion or no separation from topology null: `H1 NOT SUPPORTED` for this analysis. Do not change hypothesis or endpoint.
- Significant negative association in the frozen directional test: `H1 DIRECTIONALLY CONTRADICTED` for this specimen-level analysis.
- Insufficient endpoint coverage, graph ambiguity, invalid null family or failed invariant: `INDETERMINATE / DATA_SCHEMA_LIMITATION`; do not switch to another endpoint.

## Prohibited in this experiment

No cross-species pooling; no causal language; no E3/E4/E5 verdict; no opening the blocked *C. elegans* E4 or R20-01 line; no AI/LNN/ANN design, training, benchmarking or transfer claim; no new dataset acquisition; no changing inclusion rules, endpoints, tests, null family, number of null graphs or direction after outcomes are seen.
