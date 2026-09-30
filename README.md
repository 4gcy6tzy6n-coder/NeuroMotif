# NeuroMotif experiment archive

This repository preserves round-by-round model experiments, generated results, and lessons learned for the NeuroMotif project.

## Layout

- `model/<round>/` — runnable model or benchmark code.
- `data/results/<round>/` — generated result tables, machine-readable summaries, and verification records.
- `summery/<round>/` — protocols, scientific interpretation, strengths, failures, and corrections. The directory spelling follows the project owner's request.

Each experiment round is committed separately after its results and summary are reviewed. Results are retained as generated; later corrections and follow-ups use new versioned rounds or files.

## Evidence boundary

Synthetic benchmark outcomes are engineering results for their stated tasks. They are not biological validation or evidence of general AI benefit unless an experiment directly supports that claim. Consult each round's `summery/<round>/README.md` and `RESULTS.md` for scope and limitations.
