# M9-v1 — delayed cue/outcome association

With 500 online training episodes, eligibility trace minus no-trace averaged +0.0009 held-out accuracy (95% task-seed bootstrap CI [−0.0006, +0.0025]); only 10/30 seed averages were positive. Eligibility and BPTT were nearly equal overall (trace minus BPTT −0.0001, CI [−0.0010, +0.0008]). At 16- and 64-step delays all arms were near four-class chance. The result does not support an eligibility advantage under this training exposure and suggested the task was undertrained at longer delays.

This was a post-result exploratory architecture step based on M5's delayed teaching-signal computation, not a Fish1.5 result. The model is a trainable leaky RNN, not an LTC/LNN. It establishes no biological learning rule or general AI benefit. The separate M9-v2 folder tests higher exposure on fresh seeds; it does not overwrite this result.
