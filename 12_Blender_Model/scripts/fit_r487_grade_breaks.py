import json,sys
from pathlib import Path
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
D=json.loads((R/'reports/R487_PASSAGE_PLANE.json').read_text());q=np.array(D['controls']);test=(np.floor(q[:,0]/.4).astype(int)+3*np.floor(q[:,1]/.4).astype(int))%4==0;best=None
for a in np.arange(14.5,15.61,.1):
 for b in np.arange(16,17.61,.1):
  A=np.c_[np.ones(len(q)),q[:,0]+45,q[:,1]-24,np.maximum(0,q[:,1]-a),np.maximum(0,q[:,1]-b)];c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];err=A[~test]@c-q[~test,2];rss=float(err@err)
  if best is None or rss<best[0]:best=(rss,a,b,c,A)
_,a,b,c,A=best;e=A[test]@c-q[test,2];D.update(coefficients=c.tolist(),knots=[float(a),float(b)],rms=float(np.sqrt(np.mean(e*e))),max=float(abs(e).max()),method='Three continuous authored planar grades; two longitudinal breakpoints selected on training cells only, spatial heldout cells excluded from fitting/selection. No source surface resampling.');(R/'reports/R487_PASSAGE_PLANE.json').write_text(json.dumps(D,indent=2));print({k:D[k] for k in ['knots','rms','max','heldout']})
