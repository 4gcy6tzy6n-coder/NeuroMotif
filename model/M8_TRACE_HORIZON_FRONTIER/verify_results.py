#!/usr/bin/env python3
"""Independent structural and primary-estimand checks for M8 saved outputs."""
import csv, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'results/task_metrics.csv'
if not DATA.exists(): DATA=ROOT.parents[1]/'data/results/M8_TRACE_HORIZON_FRONTIER/task_metrics.csv'
rows=list(csv.DictReader(DATA.open()))
assert len(rows)==1350
keys={(float(r['rho']),int(r['seed']),int(r['delay']),r['arm']) for r in rows}
assert len(keys)==1350
assert all(np.isfinite(float(r['accuracy'])) for r in rows)
lookup={(float(r['rho']),int(r['seed']),int(r['delay']),r['arm']):float(r['accuracy']) for r in rows}
per_seed=[]
for s in range(30):
    vals=[lookup[(rho,s,d,'HORIZON_64')]-lookup[(rho,s,d,'HORIZON_1')]
          for rho in (0.0,0.5,0.9) for d in (4,16,64)]
    per_seed.append(float(np.mean(vals)))
SUMMARY=DATA.parent/'summary.json'
reported=json.load(SUMMARY.open())['primary']
assert np.isclose(np.mean(per_seed),reported['mean'])
assert sum(x>0 for x in per_seed)==reported['positive_seed_count']
print(json.dumps({'rows':len(rows),'unique_keys':len(keys),'all_finite':True,
                  'primary_mean_reproduced':float(np.mean(per_seed)),
                  'positive_seed_count':sum(x>0 for x in per_seed)},indent=2))
