# M8 strengths and lessons

- The question follows directly from M7's identified limitation: the eligibility trace was weaker than exact replay and its value varied with delay and input correlation.
- Each horizon has an explicit rolling-buffer implementation; the first implementation mismatch is disclosed and retained as invalid history.
- The primary comparison is paired at the task-seed level, with correlation and delay cells retained rather than treated as independent samples.
- The outcome gives a useful bounded result: longer truncated history improved over immediate-feature credit assignment on average, but did not match exact replay and did not dominate at short delay.
- The central lesson is a performance/history-size frontier, not a general AI advantage. Follow-up work should first resolve the Accelerate warnings and then compare against resource-matched online baselines under independently generated task families.
