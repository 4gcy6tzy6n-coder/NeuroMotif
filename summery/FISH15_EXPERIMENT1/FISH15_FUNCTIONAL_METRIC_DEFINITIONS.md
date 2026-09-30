# Fish1.5 functional metric definitions — retrospective freeze

**Status:** `RETROSPECTIVELY_SPECIFIED`; definitions frozen before Experiment 1 outcome computation. This contract was informed by previously inspected field names, array dimensions, code-defined timebase, trace missingness summaries, and published rise/decay results. It is not a prospective preregistration.

## Source, timebase and unit

- Source: official `data/raw/fish15/clem_zfish1_functional_data.h5`.
- Dot conditions: `dff_trials_left_dots`, `dff_trials_right_dots`.
- Sine condition arrays exist, but no per-trial stimulus waveform/phase reference or calibrated input is stored. Sine phase lag and calibrated gain are **not identifiable** and will not be computed.
- Timebase provenance: `OFFICIAL_ANALYSIS_CODE_DEFINED`. Official notebook uses `dt=0.5 s`, with sample times `arange(160)*0.5`; the HDF5 has no embedded time axis. The nominal ON interval is `[20,60) s` by that code convention.
- Sample windows (half-open): baseline `[0,20)` = indices `[0,40)`; onset search `[20,50)` = `[40,100)`; final-stimulus reference `[50,60)` = `[100,120)`; post-offset persistence `[60,70)` = `[120,140)`; post-offset decay interval `[60,80)` = `[120,160)`.
- Trials and frames are repeated measurements nested within neuron; they are never independent statistical units. Trial summaries are formed within each direction and neuron first.

## Primary endpoint

`POST_OFFSET_PERSISTENCE` is the equal-direction mean of direction-specific trial medians. For each dot-motion trial:

1. `b = mean(y[0:40])`.
2. `s = mean(y[100:120]) - b`.
3. `p = mean(y[120:140]) - b`.
4. Trial persistence fraction is `p/s`. No near-zero cutoff or response-sign exclusion is added. An exactly zero/nonfinite `s` gives an undefined trial metric; record that reason and omit only that undefined trial metric.
5. For each direction, take the median of defined trial fractions. Average the available direction medians with equal direction weight. If both directions have no defined trial value, the neuron endpoint is missing. A one-direction value remains usable and is flagged as single-direction.

The endpoint is signed: opposite-sign post-offset response yields a negative fraction. It is an observed fluorescence-trace persistence fraction under nominal code timing, not a direct neural-state or behavioral measure.

## Prespecified secondary endpoints

- `POST_OFFSET_AUC_60_70`: per-trial trapezoidal integral of baseline-subtracted dF/F over `[60,70)` using the fixed 0.5 s grid; median within direction, then equal mean across available directions.
- `STEADY_STATE_RESPONSE`: per-trial mean over `[50,60)` minus that trial's `[0,20)` baseline; median within direction, then equal mean across available directions.
- `ONSET_RISE_TIME_10_90`: from the direction-level mean trace, baseline is `[0,20)` and plateau is `[50,60)`. Search only `[20,50)` for the first 10% and first 90% fractional crossings from baseline toward plateau; linearly interpolate between adjacent samples; endpoint is `t90-t10`. If plateau equals baseline or either crossing is absent, record undefined.
- `DECAY_TAU_60_80`: per direction, fit `y(t)=b + A*exp(-(t-60)/tau)` by least squares on `[60,80)`, with `b` fixed to the direction's `[0,20)` mean, `A` unconstrained, and `tau` bounded to `[0.5,20] s`. Average valid direction estimates equally. Boundary fits are retained and flagged. This is a calcium-trace time constant, convolved with indicator kinetics; it is not a neural time constant.
- `SINE_PHASE_LAG`, `SINE_GAIN`: `NOT_IDENTIFIABLE_FROM_RELEASED_SCHEMA`; report as unavailable, never calculate from the condition name alone.

## Missingness and aggregation

A trial is window-complete for a metric only if all samples in every window used by that metric are finite. This is a schema/availability rule, not a response-magnitude filter. Require at least one usable trial metric per direction to calculate that direction's summary; do not impose a minimum response size. Record per-neuron/direction usable-trial counts and missing reasons. No interpolation or imputation is allowed. Structural cohort membership is frozen independently of functional values.

## Time interpretation and limitations

The 20–60 s stimulus window and `dt=0.5 s` are official-code conventions. They do not establish per-trial stimulus alignment. Analyses are explicitly nominally aligned. The single specimen and response-derived cell annotations prevent population-level, causal, and cell-class-independent generalization.
