# M2 Bayesian observer follow-up

## Result

This was a post-result exploratory follow-up with 1,000 episodes in each of nine synthetic hazard/noise environments and five controllers. The archived CSV contains 45,000 controller-by-episode rows; the episode is the independent unit and each episode's observation stream is shared across controllers.

The existing experiment report documents that the known-generator Bayesian observer outperformed both no-feedback and α=1 feedback in all nine environments. Paired 95% t intervals for those contrasts were positive in every environment. The report's contrast against the post-hoc selected best fixed-α arm is descriptive and optimistically biased because that arm was selected using the same outcomes.

## Interpretation and limits

The observer exactly filters the joint target/artifact state while knowing the transition and observation parameters. This demonstrates that a simple fixed feedback heuristic is not optimal for the synthetic task when the generator is known. It does not compare compute, parameter count, learning cost, or performance under unknown environments. It is not a trainable recurrent network, not a biological validation, and not evidence against the biological mechanism.

The run is explicitly post-result and exploratory, not preregistered or confirmatory. Time steps are nested within episodes and were not treated as independent observations.

## Reproducibility

The archived CSV and manifest match the source archive byte-for-byte. The source manifest's CSV SHA-256 is retained; the package also contains hashes for all listed artifacts. The published runner changes only output routing to a timestamped package-local directory.
