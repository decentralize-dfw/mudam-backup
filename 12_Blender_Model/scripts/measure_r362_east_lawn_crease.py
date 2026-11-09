from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
from scipy.optimize import least_squares
r=json.loads((R/'reports/R356_PAVILION_PLANES.json').read_text());q=np.array([c for v in r.values() for c in v['controls']]);A=np.column_stack([q[:,:2],np.ones(len(q))]);cc=np.floor(q[:,:2]/.6).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0
co=np.array([r['pavilion_east_north']['plane'],r['pavilion_east_south']['plane']]).ravel()
def predict(c):return np.maximum(A@c[:3],A@c[3:])
f=least_squares(lambda c:(predict(c)-q[:,2])[~test],co,max_nfev=500);e=(predict(f.x)-q[:,2])[test]
out=dict(planes=f.x.reshape(2,3).tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),heldout=int(test.sum()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25),method='Two independent architectural planes with continuous intersection crease. Fit only training spatial cells; held-out cells untouched; no source surface triangulation.');print(out);(R/'reports/R362_EAST_LAWN_CREASE.json').write_text(json.dumps(out,indent=2))
