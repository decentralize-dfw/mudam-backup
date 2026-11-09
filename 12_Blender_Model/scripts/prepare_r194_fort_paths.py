from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import LineString,box
lines=[('UPPER_RAMPART_WALK',[(438,597),(672,500),(790,673),(737,726),(967,1067)],1.3),('SOUTHWEST_WALK',[(381,880),(446,1005),(555,1098),(590,1105),(635,1084),(794,926)],1.8)]
out=[]
for name,pixels,width in lines:
 xy=[(-340+x*.1625,-45-y*.1625) for x,y in pixels];p=LineString(xy).buffer(width/2,cap_style='flat',join_style='round');tris=[]
 for x in range(int(p.bounds[0])-2,int(p.bounds[2])+2,2):
  for y in range(int(p.bounds[1])-2,int(p.bounds[3])+2,2):
   tris.extend(list(t.exterior.coords)[:-1] for t in shapely.constrained_delaunay_triangles(p.intersection(box(x,y,x+2,y+2))).geoms if t.area>1e-8)
 out.append(dict(name=name,pixels=pixels,width=width,triangles=tris,source='Manual centerline/width trace in R172_fort_source_top.png, registered1600px view'))
(R/'config/r194_fort_paths.json').write_text(json.dumps(out,indent=2));print([(r['name'],len(r['triangles'])) for r in out])
