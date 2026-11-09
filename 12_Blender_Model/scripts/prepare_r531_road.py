import sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
p=np.array(json.loads((R/'reports/R527_SOUTH_PAVING_PLANE.json').read_text())['controls'])
# Separate the inland road from the wall cap; retain only the low road-side strip.
p=p[(p[:,1]>.102*p[:,0]-62.4)&(p[:,2]<.052*p[:,0]-4.9)]
A=np.c_[p[:,:2],np.ones(len(p))];train=np.arange(len(p))%4!=0;c=np.linalg.lstsq(A[train],p[train,2],rcond=None)[0];e=A[~train]@c-p[~train,2]
d=dict(plane=c.tolist(),controls=p.tolist(),training=int(sum(train)),heldout=dict(count=int(sum(~train)),rms=float(np.sqrt(np.mean(e*e))),max=float(max(abs(e)))))
(R/'reports/R531_ROAD_PLANE.json').write_text(json.dumps(d,indent=2));print(d['plane'],d['training'],d['heldout'])
