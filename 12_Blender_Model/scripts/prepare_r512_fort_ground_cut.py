from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Point,Polygon
from shapely.ops import triangulate
raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());foot=Polygon(raw['footprint']);phi=math.atan2(-raw['direction'][1],-raw['direction'][0]);out=[]
for label,cx,cy,r in [('WEST',-71.05941360608443,-47.59487817095812,4.64),('SOUTH',-57.076460370468,-63.11257545086857,4.64*4.263669540042431/4.7)]:
 wedge=Polygon([(cx,cy)]+[(cx+8*math.cos(phi-math.pi/2+i*math.pi/96),cy+8*math.sin(phi-math.pi/2+i*math.pi/96)) for i in range(97)])
 cut=wedge.difference(Point(cx,cy).buffer(r,quad_segs=64));pieces=list(cut.geoms) if hasattr(cut,'geoms') else [cut];tris=[]
 for p in pieces:tris += [list(t.exterior.coords)[:3] for t in triangulate(p) if p.covers(t.representative_point())]
 out.append(dict(tower=label,center=[cx,cy],radius=r,regions=tris,outlines=[list(p.exterior.coords)[:-1] for p in pieces],source='New architectural corbel outer edge, front half only. Remove unsupported inherited earth outside reconstructed structural support; retain court-side soil.'))
(R/'reports/R512_FORT_SOIL_CUT_DOMAINS.json').write_text(json.dumps(out,indent=2));print([(q['tower'],len(q['regions'])) for q in out])
