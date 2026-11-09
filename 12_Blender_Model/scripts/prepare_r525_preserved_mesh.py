import sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles,set_precision
d=json.loads((R/'reports/R525_EDGE_PRESERVATION_DOMAINS.json').read_text());old=json.loads((R/'reports/R525_ORIGINAL_TERRACE_MESH.json').read_text());skirt=LineString([p[:2]for p in d['wall']]).buffer(1.2,quad_segs=2).intersection(box(-60,-2,-12,15));floor=unary_union([Polygon(t)for p in d['floor']for t in p['triangles']]);cutter=unary_union([Polygon(d['terraceOutline']),floor.difference(skirt)]);verts=[];faces=[];lookup={}
def ix(x,y,z):
 key=tuple(round(float(v),6)for v in (x,y,z))
 if key not in lookup:lookup[key]=len(verts);verts.append(key)
 return lookup[key]
triangles=[];coeff=[]
for f in old['triangles']:
 p=np.array([old['vertices'][i]for i in f]);poly=Polygon(p[:,:2])
 if poly.area<1e-8:continue
 triangles.append(poly);coeff.append(np.linalg.solve(np.c_[p[:,:2],np.ones(3)],p[:,2]))
from scipy.spatial import Delaunay
from shapely.strtree import STRtree
from shapely.geometry import Point
index=STRtree(triangles);remaining=set_precision(unary_union(triangles).difference(cutter).intersection(box(-27,-1.2,-13,3.6)).buffer(0),.001)
base=list(constrained_delaunay_triangles(remaining).geoms);sub=[]
original=np.unique(np.round(np.array(old['vertices'])[:,:2],6),axis=0)
for t in base:
 pts=list(t.exterior.coords)[:3]+[list(p)for p in original if t.contains(Point(*p))];pts=np.unique(np.round(pts,6),axis=0)
 if len(pts)==3:sub.append(Polygon(pts))
 else:
  for ids in Delaunay(pts).simplices:sub.append(Polygon(pts[ids]))
for t in sub:
 if t.area<1e-8:continue
 ids=[]
 for x,y in list(t.exterior.coords)[:3]:
  p=Point(x,y);candidates=[i for i in index.query(p.buffer(.002)) if triangles[i].distance(p)<.002];assert candidates
  z=max(coeff[i][0]*x+coeff[i][1]*y+coeff[i][2]for i in candidates);ids.append(ix(x,y,z))
 faces.append(ids)
(R/'reports/R525_PRESERVED_EDGE_MESH.json').write_text(json.dumps(dict(vertices=verts,faces=faces)));print(len(verts),len(faces))
