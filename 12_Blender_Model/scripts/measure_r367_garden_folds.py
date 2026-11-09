from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
from scipy.optimize import least_squares
r=json.loads((R/'reports/R366_PAVILION_GARDEN.json').read_text());q=np.array(r['controls']);A=np.column_stack([q[:,:2],np.ones(len(q))]);cc=np.floor(q[:,:2]/.6).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0
co=[.0007,.0069,-5.0678,.069,-.12,-8.11,.061,-.029,-2.57]
def predict(c):return A@c[:3]+np.maximum(0,A@c[3:6])+np.minimum(0,A@c[6:])
f=least_squares(lambda c:(predict(c)-q[:,2])[~test],co,max_nfev=1500);e=(predict(f.x)-q[:,2])[test];out=dict(coefficients=f.x.reshape(3,3).tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),heldout=int(test.sum()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25));print(out);(R/'reports/R367_PAVILION_GARDEN_FOLDS.json').write_text(json.dumps(out,indent=2))
