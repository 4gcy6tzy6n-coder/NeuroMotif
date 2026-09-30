# Experiment 1 artifact validation log

Validation performed against the generated artifacts; no biological values were recomputed by this check.

| Check | Result |
|---|---|
| primary n 82 | PASS |
| positive test not supported | PASS |
| overall indeterminate due to null | PASS |
| exact 1000 unique topologies | PASS |
| degree invariants | PASS |
| global weight multiset | PASS |
| undefined null stat count | PASS |
| metric rows primary plus sensitivity | PASS |
| correction log exists | PASS |

The analysis execution itself is recorded in `FISH15_EXPERIMENT1_PROVENANCE.json`. The topology-null invariant checks confirm exact binary in/out degrees, exact global weight multiset, and unique binary-topology hashes; the result table records that the null correlation is undefined for 861 of the 1,000 valid topologies.

| Secondary family report correction | PASS | 82 unique primary rows independently re-read; constant three-step predictor marked not estimable; all 5 finite secondary p-values independently recalculated and Holm-adjusted at 1.0. No primary statistic recomputed. |
