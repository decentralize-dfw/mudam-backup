from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon,box
rows=json.loads((R/'config/r210_ground_coverage.json').read_text());polys=[]
for r in rows:
 for t in r['triangles']:
  p=Polygon([v[:2] for v in t])
  if p.is_valid and p.area>1e-8:polys.append(p)
covered=shapely.union_all(polys,grid_size=.0001)
features=json.loads((R/'config/r176_north_footprints.json').read_text())
buildings=shapely.union_all([Polygon(r['ring']) for r in features if Polygon(r['ring']).is_valid])
missing=box(255,390,445,495).difference(covered).difference(buildings.buffer(.002))
parts=[p for p in getattr(missing,'geoms',[missing]) if p.area>.002]
out=[]
for i,p in enumerate(parts):
 out.append(dict(id=i,area=p.area,bounds=list(p.bounds),outer=list(p.exterior.coords)[:-1],triangles=[list(t.exterior.coords)[:-1] for t in shapely.constrained_delaunay_triangles(p).geoms if t.area>1e-8]))
(R/'config/r210_ground_missing.json').write_text(json.dumps(out));print('HOLES',len(out),'AREA',sum(r['area'] for r in out));print([(r['id'],round(r['area'],3),r['bounds']) for r in out])
