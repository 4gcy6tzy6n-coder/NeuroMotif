# Fish1.5 Experiment 1 figure QA

**Status:** draft figure exports verified with a documented collision-audit limitation. This is not submission-ready artwork.

## Outputs

- Main evidence figure: `FISH15_FIGURE_STRUCTURE_DYNAMICS.pdf`, `.svg`, `.tiff`.
- Descriptive robustness figure: `FISH15_FIGURE_ROBUSTNESS.pdf`, `.svg`, `.tiff`.
- Panel source tables: `FISH15_FIGURE_PANEL_A_SOURCE.csv`, `FISH15_FIGURE_PANEL_B_SOURCE.csv`, `FISH15_FIGURE_PANEL_C_SOURCE.csv`.
- Contract and legend: `FISH15_FIGURE_CONTRACT.md`, `FISH15_FIGURE_LEGEND.md`.

## Checks

| Check | Main figure | Robustness figure | Result |
|---|---|---|---|
| Static figure validator, strict mode | 20 pass, 1 warn, 0 fail | 20 pass, 1 warn, 0 fail | One target-width advisory; see below |
| PDF text/font audit | minimum 6.2 pt | minimum 6.5 pt | PASS; no glyph below 5 pt |
| Panel alignment audit | 1 comparison, 0 fail, 0 warn | Single panel; not applicable | PASS / N/A |
| Visual inspection of final TIFF | inspected | inspected | PASS; no text overlap observed |
| File format/readability | PDF, SVG, TIFF present | PDF, SVG, TIFF present | PASS |
| Automated rendered collision audit | 0 fail, 0 warn; 3 contained fill overlays | 0 fail, 0 warn | PASS |

The main figure collision audit initially found the 900 tick line crossing the `86.1%` label. The label was moved upward, both figures were re-rendered, and the final collision audit passed. The three contained fill overlays on the main figure correspond to contained text-background fills and were visually reviewed.

The strict static validator reports a width advisory because its heuristic expects a common 89 mm or 183 mm default. The contracted target is an NMI-style maximum of 180 mm, and the actual exported TIFF is 176.9 mm wide; the advisory is therefore documented rather than treated as a hard failure. The validator reports no source errors or other warnings.

## Interpretation safeguards

The figures display only the already saved Experiment 1 outputs. The plotting script reads saved result tables and does not recompute statistics. The primary association is non-supportive of the frozen positive-direction hypothesis; the combined decision remains indeterminate because most frozen topology-null statistics are undefined. One specimen supports no population-level inference. The analysis is retrospective and partially informed, as disclosed in the experiment validation and scope-incident records.

## Dimensions

At 600 dpi, the tight-bbox TIFF exports measure 176.9 mm (main figure) and 142.5 mm (robustness figure) wide. The main export meets the stated 180 mm production-width maximum. This does not establish journal acceptance or final production readiness.
