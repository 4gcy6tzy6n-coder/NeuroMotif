# M9-v2 — training-exposure optimization after M9-v1

**Classification:** post-result exploratory optimization. M9-v1 outcomes were inspected before this version. This is not confirmatory and does not validate a biological rule.

## Reason for this version

M9-v1 used 500 training episodes and produced held-out accuracy near four-class chance at delays 16 and 64 for every arm (BPTT means 0.2699 and 0.2645; chance = 0.25). Its eligibility-minus-no-trace primary contrast was +0.0009 (95% seed-bootstrap interval [−0.0006, +0.0025]). The result does not demonstrate an eligibility advantage, and weak task learning limits interpretation at longer delays.

## Sole change from M9-v1

Increase training exposure from 500 to **3,000 online episodes per task-seed × delay × arm**, keeping the task, architecture, delay grid, optimizer, learning rate, trace decay, clipping, test size, arms, bootstrap method, and all other parameters unchanged. Use a fresh, disjoint task-seed range **200–229** (M9-v1 used 100–129). No learning-rate, trace-decay, initialization, or task adjustments are allowed in this version.

All M9-v1 definitions and formulas are inherited exactly from [`../m9_m5_eprop_recurrent_association/M9_CONTRACT.md`](../m9_m5_eprop_recurrent_association/M9_CONTRACT.md), except for the increased training episode count, new seed range, and the viability gate below.

## Prespecified viability gate

For each delay separately, BPTT mean held-out accuracy is estimated over the 30 task seeds with the same paired-seed bootstrap procedure. A delay is `TASK_VIABLE` only if the 95% bootstrap lower bound is strictly above four-class chance (0.25). The eligibility contrast at a nonviable delay is descriptive only. The primary all-delay eligibility comparison is interpretable only if all three delays pass this gate; otherwise the whole M9-v2 result is classified `INCONCLUSIVE_TASK_NOT_LEARNABLE_ACROSS_GRID`.

## Primary analysis and stop

Primary contrast remains `ELIGIBILITY_TRACE − NO_TRACE`, averaged equally over delays within each task seed and then over 30 seeds; report the 20,000-resample task-seed bootstrap interval and positive-seed count. Always report BPTT and per-delay results. Run once and stop; no additional tuning is authorized under this version.
