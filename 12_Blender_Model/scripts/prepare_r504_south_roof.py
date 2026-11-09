from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
edge=next(t for t in json.loads((R/'reports/R503_TOWER_EDGE_CIRCLE_FITS.json').read_text()) if t['tower']=='SOUTH')['trials'][1]
cx,cy,r=edge['fit'];p=np.array(json.loads((R/'reports/R418_TOWER_CAP_PLANES.json').read_text())['SOUTH']['samples']);rr=np.linalg.norm(p[:,:2]-[cx,cy],axis=1);M=np.c_[np.ones(len(p)),rr];keys=np.floor(p[:,:2]/.4).astype(int);test=(keys[:,0]+3*keys[:,1])%4==0;coef=np.linalg.lstsq(M[~test],p[~test,2],rcond=None)[0];e=M[test]@coef-p[test,2];d=dict(edge=edge,roofPlane=coef.tolist(),roofCheck=dict(training=int((~test).sum()),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max())),limits=['Scan contour smears edges; radius varies 4.204–4.293m with edge threshold. Chosen middle threshold is not surveyed certainty.','Existing photo-proportioned openings preserved by coherent radial transform.'])
(R/'reports/R504_SOUTH_ROOF_PARAMETERS.json').write_text(json.dumps(d,indent=2));print(d['roofCheck'])
