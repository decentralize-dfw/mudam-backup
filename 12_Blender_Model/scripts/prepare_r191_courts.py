from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon,box
features=json.loads((R/'config/r176_north_footprints.json').read_text())
buildings=shapely.union_all([Polygon(r['ring']).buffer(.02) for r in features if Polygon(r['ring']).is_valid])
domains=[('MAMA_FORECOURT',[(151,782),(402,647),(516,701),(558,769),(434,868),(334,881),(277,938),(200,942)]),('NOVOTEL_WEST_COURT',[(575,730),(646,728),(760,872),(842,997),(788,1050),(698,932)])]
out=[]
for name,pixels in domains:
 p=Polygon([(255+x*.1125,525-y*.1125) for x,y in pixels]).difference(buildings)
 if not p.is_valid:raise RuntimeError(name)
 triangles=[]
 for x in range(int(p.bounds[0])-1,int(p.bounds[2])+2,2):
  for y in range(int(p.bounds[1])-1,int(p.bounds[3])+2,2):
   clipped=p.intersection(box(x,y,x+2,y+2))
   triangles.extend(list(t.exterior.coords)[:-1] for t in shapely.constrained_delaunay_triangles(clipped).geoms if t.area>1e-8)
 out.append(dict(name=name,pixels=pixels,triangles=triangles,area=p.area,source='R190_roofs_source_top.png; manually traced paving limits, OSM building interiors subtracted',limits=['Tree-obscured pavement edges remain approximate','Asphalt material selected from visible source appearance']))
(R/'config/r191_courtyard_domains.json').write_text(json.dumps(out,indent=2));print([(r['name'],r['area'],len(r['triangles'])) for r in out])
