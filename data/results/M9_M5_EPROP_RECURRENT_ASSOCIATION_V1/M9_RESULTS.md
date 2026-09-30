# M9 — M5 eligibility in a trainable recurrent association task

**Classification:** post-result exploratory AI study. This is not biological validation or general transfer.

Primary paired task-seed contrast (`ELIGIBILITY_TRACE − NO_TRACE`, equally averaged over delays 4/16/64): **+0.0009** accuracy (95% task-seed bootstrap CI [-0.0006, +0.0025]); 10/30 task seeds positive.

Equal-delay mean held-out accuracy:
- ELIGIBILITY_TRACE: 0.3029
- NO_TRACE: 0.3020
- BPTT: 0.3030
- ELIGIBILITY_TRACE − BPTT: -0.0001 (95% CI [-0.0010, +0.0008])
- NO_TRACE − BPTT: -0.0010 (95% CI [-0.0024, +0.0002])

| Delay | Trace − no-trace | 95% CI | Positive seeds |
|---:|---:|---:|---:|
| 4 | +0.0045 | [+0.0021, +0.0075] | 14/30 |
| 16 | +0.0003 | [-0.0019, +0.0025] | 8/30 |
| 64 | -0.0021 | [-0.0047, +0.0003] | 4/30 |

Task seeds are the independent units; episodes and delays are paired repeated observations. The model is a fully trainable leaky RNN, not an LTC/LNN implementation. Eligibility is a simplified local learning abstraction inspired by delayed teaching signals. Preserve the BPTT comparison and all negative/uncertain results in interpretation.
