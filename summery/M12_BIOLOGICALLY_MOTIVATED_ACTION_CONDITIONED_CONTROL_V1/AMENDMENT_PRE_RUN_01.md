# M12 pre-run contract clarification 01

**Status:** frozen before implementation and before outcome generation. The original `CONTRACT.md` and its SHA-256 remain unchanged. This amendment fills analysis and reproducibility details that were underspecified; it does not change the task, model arms, endpoints, primary contrast, threshold, independent unit, or disposition rules.

## Statistical details

For every planned contrast, compute one paired difference per task-seed block after averaging that seed's episode metrics equally. The primary 95% interval is the percentile bootstrap over the 40 paired seed-block differences, 20,000 resamples, using analysis seed `812999`. For the two prespecified secondary contrasts, report the same paired-seed percentile-bootstrap 95% intervals and two-sided paired t-test p-values across the 40 seed-block differences. Apply Holm correction to those two secondary p-values as one family at familywise alpha `0.05`. The primary contrast is judged by its interval and the contract's 2% threshold, without a primary p-value.

## Random-stream and model details

For task-seed block `s`, derive disjoint streams by NumPy `SeedSequence([s, stream_id])`: `stream_id=1` for training-episode generation, `2` for test-target/noise generation, `3` for model initialization/training minibatch order, and `4` for motor-channel permutations. Model arms use stable arm IDs and distinct initialization substreams under stream 3; all arms share the exact same generated train and test trajectories. Recurrent hidden states initialize to zero for each episode. The 7-unit gated model uses the explicit equations in `CONTRACT.md`; the generic model is `torch.nn.GRUCell` with 6 units and a linear scalar readout. Both action readouts are `0.25*tanh(linear(h_t))`. Use PyTorch Adam defaults (`betas=(0.9,0.999)`, `eps=1e-8`, `weight_decay=0`) at the frozen learning rate; no gradient clipping or scheduler is used. The final epoch is authoritative.

For the permuted-input arm, within each training minibatch and test batch, independently permute the previous-action input across episodes at each time step. The actual unpermuted action still updates controller position and determines the environment's observation-noise scale.

## Interpretation

This is a pre-outcome implementation clarification. It is not a new experiment version and was made without reading any M12 generated performance output. All later deviations must be logged as implementation issues and cannot be used to choose a preferred result.
