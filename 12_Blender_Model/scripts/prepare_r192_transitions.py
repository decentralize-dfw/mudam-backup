from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon,Point,box
rows=json.loads((R/'config/r191_measured_courts.json').read_text());out=[]
features=json.loads((R/'config/r176_north_footprints.json').read_text());buildings=shapely.union_all([Polygon(r['ring']) for r in features if Polygon(r['ring']).is_valid])
for row in rows:
 p=shapely.union_all([Polygon(t) for t in row['triangles']]).simplify(.001);band=p.buffer(2,join_style='mitre').difference(p).difference(buildings);triangles=[]
 for x in range(int(band.bounds[0])-1,int(band.bounds[2])+2):
  for y in range(int(band.bounds[1])-1,int(band.bounds[3])+2):
   for t in shapely.constrained_delaunay_triangles(band.intersection(box(x,y,x+1,y+1))).geoms:
    if t.area>1e-8:triangles.append([[*v,min(1,p.distance(Point(v))/2)] for v in list(t.exterior.coords)[:-1]])
 cuts=[list(t.exterior.coords)[:-1] for t in shapely.constrained_delaunay_triangles(band).geoms if t.area>1e-8]
 out.append(dict(name=row['name'],origin=row['origin'],plane=row['plane'],triangles=triangles,cuts=cuts,source='2m constructed terrain transition from measured courtyard plane to existing DEM; not surveyed landscaping'))
(R/'config/r192_court_transitions.json').write_text(json.dumps(out));print([(r['name'],len(r['triangles']),len(r['cuts'])) for r in out])
