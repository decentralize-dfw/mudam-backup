from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from shapely.geometry import Point
from shapely.ops import triangulate
fit=next(t for t in json.loads((R/'reports/R444_TOWER_ROOF_EDGE_DIAGNOSTIC.json').read_text()) if t['tower']=='WEST')['fit'];cx,cy=fit[:2];p=np.array(json.loads((R/'reports/R418_TOWER_CAP_PLANES.json').read_text())['WEST']['samples']);rr=np.linalg.norm(p[:,:2]-[cx,cy],axis=1);M=np.c_[np.ones(len(p)),rr];keys=np.floor(p[:,:2]/.4).astype(int);test=(keys[:,0]+3*keys[:,1])%4==0;coef=np.linalg.lstsq(M[~test],p[~test,2],rcond=None)[0];e=M[test]@coef-p[test,2];poly=Point(-71.5,-47.6).buffer(4.525,quad_segs=48).difference(Point(cx,cy).buffer(4.305,quad_segs=48));parts=list(poly.geoms) if hasattr(poly,'geoms') else [poly];pieces=[]
for a in parts:
 pieces.append(dict(outline=list(a.exterior.coords)[:-1],triangles=[list(t.exterior.coords)[:3] for t in triangulate(a) if a.covers(t.representative_point())]))
d=dict(center=[cx,cy],radius=4.7,roofPlane=coef.tolist(),roofCheck=dict(training=int((~test).sum()),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max())),contact=pieces,limits=['Existing 4.7m eave radius retained: scan edge fit uncertainty too high to justify radius change.','Centre from independent roof class point fit; source surface and edge centre agree within about 0.13m.'])
(R/'reports/R508_WEST_TOWER_PARAMETERS.json').write_text(json.dumps(d,indent=2));print(d['roofCheck'])
