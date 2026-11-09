import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union,split
from shapely import constrained_delaunay_triangles,set_precision
p=np.array(json.loads((R/'reports/R544_WEST_GAP_SOURCE_CONTROLS.json').read_text()));p=p[p[:,1]<=4.25];A=np.c_[p[:,:2],np.ones(len(p)),np.maximum(p[:,1]-3.5,0)];train=np.arange(len(p))%4!=0;c=np.linalg.lstsq(A[train],p[train,2],rcond=None)[0];res=A@c-p[:,2]
polys=[Polygon(t)for t in json.loads((R/'reports/R544_EXISTING_COVERAGE.json').read_text())if Polygon(t).area>1e-8];gap=set_precision(box(-30.8,1.5,-26.9,4.4).difference(unary_union(polys)),.0001);parts=split(gap,LineString([(-40,3.5),(-20,3.5)]));parts=[p for p in parts.geoms if p.area>.01];tris=[list(t.exterior.coords)[:3]for p in parts for t in constrained_delaunay_triangles(p).geoms]
(R/'reports/R544_GAP_DESIGN.json').write_text(json.dumps(dict(triangles=tris,coefficients=c.tolist(),area=sum(p.area for p in parts),heldoutCount=int((~train).sum()),heldoutRMS=float(np.sqrt(np.mean(res[~train]**2))),heldoutMax=float(max(abs(res[~train])))),indent=2))
