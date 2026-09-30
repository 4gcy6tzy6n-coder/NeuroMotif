# M8 equal-history-budget replay comparison

**Task code:** `M8_MEMORY_MATCHED_REPLAY_ANALYSIS`  
**Status:** post-result exploratory analysis reusing the M8 outputs and seeds.

Across the nine correlation × delay conditions, exact replay exceeded the horizon arm with the same nominal feature-history budget (`HORIZON_D`) by **0.3082 accuracy** on average (95% paired task-seed bootstrap interval `[0.3019, 0.3142]`; all 30 seed averages favored replay). The contrast grows with delay: +0.2079 at D=4, +0.2895 at D=16, and +0.4271 at D=64; all delay-specific 95% intervals exclude zero and all 30 seed means at each delay favor replay.

| Delay | Matched horizon | Active history values per arm | Exact replay − horizon accuracy (95% paired task-seed bootstrap interval) |
|---:|---:|---:|---:|
| 4 | H4 | 256 | +0.2079 `[+0.2008, +0.2149]` |
| 16 | H16 | 1,024 | +0.2895 `[+0.2804, +0.2986]` |
| 64 | H64 | 4,096 | +0.4271 `[+0.4196, +0.4344]` |

The pattern is consistent across all nine rho × delay cell means. This weakens a claim that the trace aggregation itself is more effective than retaining the same nominal number of recent feature vectors in this task family. It does not establish that replay is universally better: this analysis reuses M8's synthetic teacher task and estimates active learner-state from the stated buffer accounting rather than measuring total process memory. Task-array storage and delayed prediction history are shared by arms and excluded equally.

This is a post-result secondary analysis, not an independent experiment or confirmatory inference. It supports the narrow conclusion that, on these fixed synthetic tasks, exact replay used the same nominal feature-history budget more effectively than an exponentially weighted horizon summary. It provides no biological validation, cross-task generalization, or publication-level novelty evidence.
