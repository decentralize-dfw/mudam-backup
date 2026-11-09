import sys,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon
from shapely import constrained_delaunay_triangles
parts=json.loads((R/'reports/R549_GAP_CONTROLS.json').read_text())
for k,q in enumerate(parts):
 p=np.array(q['controls']);p=p[(p[:,2]<-3.1)&(p[:,2]>-3.6)];A=np.c_[p[:,:2],np.ones(len(p))];tr=np.arange(len(p))%4!=0;c=np.linalg.lstsq(A[tr],p[tr,2],rcond=None)[0];r=A@c-p[:,2];q['plane']=c.tolist();q['heldoutCount']=int((~tr).sum());q['heldoutRMS']=float(np.sqrt(np.mean(r[~tr]**2)));q['heldoutMax']=float(max(abs(r[~tr])));q['triangles']=[list(t.exterior.coords)[:3]for t in constrained_delaunay_triangles(Polygon(q['outline'])).geoms];q['method']='Independent exterior grade plane from exposed floor observations between -3.6 and -3.1m; higher roof/curb observations not treated as floor. Continuation under overhanging glass is inferred, not directly observed.'
(R/'reports/R549_GAP_PLANES.json').write_text(json.dumps(parts,indent=2))
