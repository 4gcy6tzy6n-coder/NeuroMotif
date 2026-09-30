# Fish1.5 secondary-association reporting correction

**Type:** limited post-run reporting correction to the pre-specified secondary family; it does not change the Experiment 1 primary endpoint, predictor, null, or decision.

## Issue

The stored `FISH15_SECONDARY_ASSOCIATIONS.csv` reported `holm_adjusted_p=1.0` for `three_step_return_strength`, although that predictor is constant across all 82 primary nodes and Spearman rho / raw p are both undefined. A constant predictor is **not an estimable secondary test**. Its displayed `1.0` was a conservative placeholder from the old Holm loop and could be mistaken for an observed test result.

## Correction

The original CSV is preserved unchanged. `FISH15_SECONDARY_ASSOCIATIONS_CORRECTED.csv` reports the three-step metric as `NOT_ESTIMABLE_CONSTANT_PREDICTOR` and uses `NA` for rho, raw p, and adjusted p. For the five estimable tests, Holm correction retains the frozen family size of six by assigning the non-estimable member a conservative p=1 placeholder in the adjustment calculation. This changes no finite-test adjusted values; all remain 1.0. The correction script reads only the existing frozen 82-node metric table and recomputes only the already pre-specified secondary family.

## Corrected interpretation

The five estimable secondary associations are all small and negative (rho range -0.1124 to -0.0698), with Holm-adjusted p=1.0. The three-step return predictor is undefined because it is zero for all primary nodes. No secondary metric supports a positive substitute for the frozen primary hypothesis. This is a within-one-specimen exploratory result, not independent animal replication.

## Reproduction

Run `python3 scripts/verify_fish15_secondary_associations.py` from the project root. The script asserts 82 unique primary IDs and finite primary persistence values, calculates only the six frozen secondary descriptors, applies the stated conservative family adjustment, and writes the corrected table.

No primary test, topology null, robustness endpoint, or model was rerun.

## Integrity hashes

- `frozen_metrics_sha256`: `e20c25b90dcba640b0118c1902b76c0c33d89c4969bb5ea9df053d13048550b3`
- `original_secondary_table_sha256`: `8e182a34db7699b2abc397872442132e7740784c835fd8824c140ef7f9b0b081`
- `corrected_secondary_table_sha256`: `2cd960b5922bd143e52e3eff0e95d4a23822308a2d26d8062c90f53fe3e53f0a`
- `correction_script_sha256`: `0e10311448c53ef2b90399bafa67d525a75a8b265d16c07ec76cfe94f1bb4558`
- `runner_sha256`: `d70e8eb43662be7bbe488b9e98806a7e68e30bbf71ca87f086228f09f3077fb6`
