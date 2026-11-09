from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
d=json.loads((R/'reports/R394_TOWER_JUNCTION.json').read_text());p=np.array(d['samples']);out={}
for name,condition in [('tower_forecourt',p[:,0]+p[:,1]<-112),('end_shoulder',(p[:,0]+p[:,1]>=-112)&(p[:,0]+p[:,1]<-108))]:
 q=p[condition];A=np.column_stack((q[:,:2],np.ones(len(q))));cc=np.floor(q[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0;coef=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];e=A[test]@coef-q[test,2];out[name]=dict(plane=coef.tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),heldout=int(test.sum()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25),bounds=[q[:,:2].min(axis=0).tolist(),q[:,:2].max(axis=0).tolist()])
(R/'reports/R399_FRONT_COURT_PLANES.json').write_text(json.dumps(out,indent=2));print(out)
