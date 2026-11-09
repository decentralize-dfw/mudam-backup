import json,sys
from pathlib import Path
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
from shapely.geometry import Polygon,Point
D=json.loads((R/'reports/R487_LOWER_PASSAGE_GRADE.json').read_text());poly=Polygon(D['outline']).intersection(Polygon([(-56,12),(-37,31),(-27,31),(-46,12)]))
q=np.array(D['controls']);q=np.array([p for p in q if poly.buffer(-.45).contains(Point(p[:2]))]);test=(np.floor(q[:,0]/.4).astype(int)+3*np.floor(q[:,1]/.4).astype(int))%4==0
A=np.c_[np.ones(len(q)),q[:,0]+45,q[:,1]-24,np.minimum(0,q[:,1]-17)];c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];e=A[test]@c-q[test,2]
D=dict(outline=list(poly.exterior.coords)[:-1],coefficients=c.tolist(),controls=q.tolist(),heldout=int(test.sum()),training=int((~test).sum()),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),method='Independent four-coefficient continuous plane/ramp with source-observed south break at y17, ground-class interior control cells and deterministic withheld cells. Polygon excludes historic retaining wall.',accepted=False)
(R/'reports/R487_PASSAGE_PLANE.json').write_text(json.dumps(D,indent=2));print({k:v for k,v in D.items() if k not in ['outline','controls']})
