#!/usr/bin/env python3
"""Compare canonical M8 CSV outputs across numerical runtimes."""
import csv, json, sys
from pathlib import Path
import numpy as np
if len(sys.argv) != 3: raise SystemExit('usage: compare_runtime_outputs.py OLD.csv NEW.csv')
def load(path):
    return {(r['rho'],r['seed'],r['delay'],r['arm']):float(r['accuracy']) for r in csv.DictReader(Path(path).open())}
a,b=load(sys.argv[1]),load(sys.argv[2])
assert a.keys()==b.keys(), f'condition-key mismatch: {len(a)} vs {len(b)}'
diff=np.array([a[k]-b[k] for k in a])
report={'old_rows':len(a),'new_rows':len(b),'exact_accuracy_matches':int(np.count_nonzero(diff==0)),
        'max_absolute_accuracy_difference':float(np.max(np.abs(diff))),'all_finite':bool(np.isfinite(diff).all())}
print(json.dumps(report,indent=2))
if not report['all_finite'] or report['max_absolute_accuracy_difference'] != 0: raise SystemExit(1)
