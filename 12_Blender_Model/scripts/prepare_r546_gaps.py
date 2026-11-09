import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from shapely.geometry import Polygon,Point
from shapely import constrained_delaunay_triangles
parts=json.loads((R/'reports/R546_GAP_CONTROLS.json').read_text())
for k,part in enumerate(parts):
 poly=Polygon(part['outline']);p=np.array([r for r in part['controls']if poly.buffer(.001).covers(Point(*r[:2]))]);A=np.c_[p[:,:2],np.ones(len(p))];tr=np.arange(len(p))%4!=0;c=np.linalg.lstsq(A[tr],p[tr,2],rcond=None)[0];res=A@c-p[:,2];part['plane']=c.tolist();part['heldoutCount']=int((~tr).sum());part['heldoutRMS']=float(np.sqrt(np.mean(res[~tr]**2)));part['heldoutMax']=float(max(abs(res[~tr])));part['triangles']=[list(t.exterior.coords)[:3]for t in constrained_delaunay_triangles(poly).geoms];print(k,len(p),c,part['heldoutRMS'],part['heldoutMax'])
(R/'reports/R546_GAP_PLANES.json').write_text(json.dumps(parts,indent=2))
