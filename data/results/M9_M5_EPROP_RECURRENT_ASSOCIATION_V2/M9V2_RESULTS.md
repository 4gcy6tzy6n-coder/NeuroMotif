# M9-v2 — M5 eligibility in a trainable recurrent association task

**Classification:** post-result exploratory AI study. This is not biological validation or general transfer.

Primary paired task-seed contrast (`ELIGIBILITY_TRACE − NO_TRACE`, equally averaged over delays 4/16/64): **+0.0906** accuracy (95% task-seed bootstrap CI [+0.0828, +0.0988]); 30/30 task seeds positive.

Equal-delay mean held-out accuracy:
- ELIGIBILITY_TRACE: 0.4908
- NO_TRACE: 0.4002
- BPTT: 0.5023
- ELIGIBILITY_TRACE − BPTT: -0.0114 (95% CI [-0.0193, -0.0037])
- NO_TRACE − BPTT: -0.1020 (95% CI [-0.1135, -0.0907])

| Delay | Trace − no-trace | 95% CI | Positive seeds |
|---:|---:|---:|---:|
| 4 | +0.1189 | [+0.1100, +0.1283] | 30/30 |
| 16 | +0.1420 | [+0.1223, +0.1636] | 30/30 |
| 64 | +0.0109 | [-0.0040, +0.0273] | 16/30 |

Task seeds are the independent units; episodes and delays are paired repeated observations. The model is a fully trainable leaky RNN, not an LTC/LNN implementation. Eligibility is a simplified local learning abstraction inspired by delayed teaching signals. Preserve the BPTT comparison and all negative/uncertain results in interpretation.
