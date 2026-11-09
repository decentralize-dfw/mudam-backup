from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon
domains=json.loads((R/'config/r213_access_surfaces.json').read_text());domains=[r for r in domains if not r['name'].startswith('SOUTH_CONCRETE')]
cut=shapely.union_all([Polygon(t) for r in domains for t in r['cuts']]);out=[]
for row in json.loads((R/'config/r213_cut_input.json').read_text()):
 region=Polygon([(-85+x*.1,490-y*.1) for x,y in [(695,315),(1260,550),(1240,770),(815,1160),(460,1270),(530,940),(585,740)]]) if row['name'].startswith('R177_ROAD_') else cut
 records=[]
 for t in row['triangles']:
  p=Polygon([v[:2] for v in t['points']])
  if not p.is_valid or p.area<1e-9 or not p.intersects(region):continue
  remain=p.difference(region);triangles=[list(a.exterior.coords)[:-1] for a in shapely.constrained_delaunay_triangles(remain).geoms if a.area>1e-9]
  records.append(dict(index=t['index'],triangles=triangles))
 out.append(dict(name=row['name'],replacements=records))
(R/'config/r213_cut_replacements.json').write_text(json.dumps(out));print([(r['name'],len(r['replacements'])) for r in out])
