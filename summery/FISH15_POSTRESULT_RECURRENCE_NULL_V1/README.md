# Fish1.5 recurrence-conditioned null — strengths and failure lessons

## Strengths

- Diagnosed the original null failure: 31 directed edges on 82 nodes yield only two reciprocal dyads; the frozen predictor is zero for 78 neurons, so unconstrained degree rewiring commonly makes it constant.
- The conditional exploratory null preserved exact binary degrees and exact per-node weighted in/out strengths by swapping only same-weight edges; it also conditioned on the observed reciprocal-dyad count rather than relaxing that constraint after seeing outputs.
- Generated 1,000 unique, finite-statistic topology states. Independent summary recomputation reproduced the observed rho, null mean/quantiles, and empirical tail counts from saved tables.
- Preserved the original primary test and explicitly stated that the null conditions away the amount of recurrence; it cannot test recurrence enrichment.

## Failures and limits

- The method was selected after the original result and null degeneracy were known. It is outcome-informed and exploratory.
- Topology states are serially correlated: lag-1 statistic autocorrelation is 0.714 and approximate effective sample size is only about 150 from 1,000 saved graphs. Ten-times-edge-count thinning was insufficient to establish good mixing.
- Edge lists were not saved per graph. The verifier checks reported invariant flags and audits the implementation logic, but cannot independently reconstruct each state from an edge-list artifact.
- The primary association is negative and nonsignificant (`rho=-0.1096`, directional `p=0.8337`; interval crosses zero). Neither result proves that recurrence is biologically absent.
- Single specimen, retrospective outcome exposure, sparse induced graph and outcome-derived annotations prevent population-level, causal or confirmatory claims.

## Next useful step

Do not keep tuning this null against the observed association. If the project later needs this conditional comparison, write a separately versioned protocol that saves every edge state and has an outcome-independent mixing diagnostic/ESS stopping rule before sampling. First decide whether additional graph sampling can change any substantive claim; the current data cannot support a positive motif-to-transfer story.
