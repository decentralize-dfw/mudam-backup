import sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
from shapely import set_precision
p=unary_union([Polygon(t)for t in json.loads((R/'reports/R549_COVERAGE.json').read_text())if Polygon(t).area>1e-8]);g=set_precision(box(-25,-20,5,15).difference(p),.0001);parts=list(g.geoms)if hasattr(g,'geoms')else[g];parts=[p for p in parts if p.area>.1];rows=[]
for p in parts:
 pts=[]
 for ix in range(121):
  for iy in range(141):
   x=-25+ix*.25;y=-20+iy*.25
   if p.contains(Point(x,y)):pts.append([x,y])
 rows.append(dict(outline=list(p.exterior.coords),area=p.area,samples=pts));print(p.area,p.bounds,len(pts))
(R/'reports/R549_GAP_FOOTPRINT.json').write_text(json.dumps(rows,indent=2))
