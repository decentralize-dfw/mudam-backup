import json,sys,numpy as np
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
pix=[(205,346),(245,402),(291,464),(344,532),(415,620),(530,542),(471,480),(424,497),(395,449),(352,407),(321,368),(308,343),(331,302),(368,264),(300,305)]
poly=Polygon([(-59+u*.038,27-v*.038)for u,v in pix]);assert poly.is_valid
old=json.loads((R/'reports/R586_EXISTING_TERRACE_TOP.json').read_text());covered=unary_union([Polygon([v[:2]for v in t])for t in old]);gap=poly.difference(covered)
p=np.array(json.loads((R/'reports/R586_APRON_CONTROLS.json').read_text()));p=p[(p[:,2]>-4)&(p[:,2]<-3.2)];A=np.c_[p[:,:2],np.ones(len(p))];train=np.arange(len(p))%4!=0;c=np.linalg.lstsq(A[train],p[train,2],rcond=None)[0];e=A[~train]@c-p[~train,2]
tri=[list(t.exterior.coords)[:3]for g in (gap.geoms if hasattr(gap,'geoms')else[gap])if g.area>.01 for t in constrained_delaunay_triangles(g).geoms]
d=dict(area=gap.area,triangles=tri,plane=c.tolist(),heldoutCount=int(sum(~train)),heldoutRMS=float(np.sqrt(np.mean(e*e))),heldoutMax=float(max(abs(e))),outline=list(poly.exterior.coords),source='R586 same-camera source top view; independently fitted apron plane, no copied source mesh. Outline visual trace, occluded edges provisional.',accepted=False)
(R/'reports/R586_APRON_DESIGN.json').write_text(json.dumps(d,indent=2));print({k:v for k,v in d.items()if k not in ('triangles','outline')})

