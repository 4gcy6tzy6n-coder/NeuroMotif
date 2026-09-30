#!/usr/bin/env python3
"""Audit frozen Fish1.5 secondary associations and report non-estimable tests explicitly."""
from __future__ import annotations
import csv
import math
from pathlib import Path
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / 'results/experiment1/FISH15_NEURON_METRICS.csv'
OUT = ROOT / 'results/experiment1/FISH15_SECONDARY_ASSOCIATIONS_CORRECTED.csv'
METRICS_FROZEN = (
    'in_strength', 'out_strength', 'reciprocal_strength',
    'reciprocal_fraction', 'two_step_return_strength',
    'three_step_return_strength',
)

with METRICS.open(newline='', encoding='utf-8') as f:
    rows = [r for r in csv.DictReader(f) if r['cohort'] == 'primary82']
assert len(rows) == 82
assert len({r['functional_id'] for r in rows}) == 82
assert all(math.isfinite(float(r['dots_persistence'])) for r in rows)
y = [float(r['dots_persistence']) for r in rows]
results = []
for metric in METRICS_FROZEN:
    x = [float(r[metric]) for r in rows]
    if len(set(x)) < 2:
        results.append({'metric': metric, 'n': len(rows), 'unique_predictor_values': len(set(x)),
                        'rho': 'NA', 'two_sided_p_unadjusted': 'NA',
                        'holm_adjusted_p': 'NA', 'status': 'NOT_ESTIMABLE_CONSTANT_PREDICTOR'})
    else:
        test = spearmanr(x, y)
        results.append({'metric': metric, 'n': len(rows), 'unique_predictor_values': len(set(x)),
                        'rho': f'{float(test.statistic):.15g}',
                        'two_sided_p_unadjusted': f'{float(test.pvalue):.15g}',
                        'holm_adjusted_p': '', 'status': 'ESTIMABLE'})

# Keep the frozen family size of six: use p=1 as a conservative placeholder for
# the non-estimable constant predictor, but do not report its adjusted value as a test.
finite = [(i, float(r['two_sided_p_unadjusted'])) for i, r in enumerate(results)
          if r['status'] == 'ESTIMABLE']
ordered = sorted(finite, key=lambda pair: pair[1])
previous = 0.0
m = len(METRICS_FROZEN)
for rank, (i, p) in enumerate(ordered):
    adjusted = min(1.0, max(previous, (m - rank) * p))
    results[i]['holm_adjusted_p'] = f'{adjusted:.15g}'
    previous = adjusted

with OUT.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['metric', 'n', 'unique_predictor_values', 'rho',
        'two_sided_p_unadjusted', 'holm_adjusted_p', 'status'])
    writer.writeheader(); writer.writerows(results)
print(f'Wrote {OUT}')
for r in results:
    print(r)
