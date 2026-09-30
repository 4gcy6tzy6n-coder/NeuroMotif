# M8 implementation correction log

The first exploratory execution computed each horizon update by slicing the complete in-memory training feature array. Although the mathematical window was truncated, the implementation did not enforce the contract's per-horizon history-buffer boundary. The initial outputs are preserved in `results_v0_invalid_unbounded_history/` and must not be treated as the final M8 result.

The runner now maintains a rolling buffer capped at each horizon and forms the eligibility vector only from that buffer. Exact replay retains the delayed example feature as its higher-memory reference. This is a post-result implementation correction: the initial output was visible before correction, so the rerun is outcome-informed even though the correction addresses a code-contract mismatch rather than tuning the hypothesis or endpoints.

The initial run also emitted NumPy matmul overflow/invalid warnings while all saved accuracies were finite. The corrected run must be inspected for non-finite weights, metrics, and warnings before any result is interpreted.
