import sys,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
from shapely import set_precision,constrained_delaunay_triangles
rows=[]
for reg in json.loads((R/'reports/R557_REGION_COVERAGE.json').read_text()):
 poly=box(*reg['bounds']).difference(unary_union([Polygon(t)for t in reg['triangles']if Polygon(t).area>1e-8]));poly=set_precision(poly,.0001);parts=list(poly.geoms)if hasattr(poly,'geoms')else[poly]
 for i,p in enumerate(parts):
  if p.area<.02:continue
  samples=[];samplepoly=p.buffer(.12)if reg['name']=='WEST_APPROACH'else p;a,b,c,d=samplepoly.bounds
  for x in np.arange(a+.025,c,.05)if reg['name']=='WEST_APPROACH'else np.arange(a+.06,c,.15):
   for y in np.arange(b+.025,d,.05)if reg['name']=='WEST_APPROACH'else np.arange(b+.06,d,.15):
    if samplepoly.contains(Point(x,y)):samples.append([x,y])
  rows.append(dict(name=reg['name']+'_'+str(i),area=p.area,outline=list(p.exterior.coords),triangles=[list(t.exterior.coords)[:3]for t in constrained_delaunay_triangles(p).geoms],samples=samples));print(rows[-1]['name'],p.area,p.bounds,len(samples))
(R/'reports/R557_GAP_DOMAINS.json').write_text(json.dumps(rows,indent=2))
