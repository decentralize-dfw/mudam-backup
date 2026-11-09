from pathlib import Path
import sys,json
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import shapely
from shapely.geometry import Polygon,LineString
from shapely.ops import split
D=json.loads((R/'reports/R565_CONTINUOUS_CAP_PLANES.json').read_text());c=D['coefficients'];a,b,k=json.loads((R/'reports/R529_SOUTH_FACE_PLANE.json').read_text())['plane']
def z(x,y):return c[0]+c[1]*(x-49.5)+c[2]*(y+58)+c[3]*max(x-54.5,0)+c[4]*max(x-56,0)
def front(x):return(a*x+b*(z(x,0))+k)/(1-b*c[2])
xs=[49.04445,54.5,56,64,72.13087];ring=[(49.5,-52.53),(49.5,-57.5)]+[(x,front(x))for x in xs]+[(x,front(x)+2)for x in reversed(xs[1:])]+[(50.5,front(50.5)+2),(50.5,-52.53)]
pol=Polygon(ring);assert pol.is_valid;parts=[pol]
for x in [54.5,56,64]:parts=[q for p in parts for q in split(p,LineString([(x,-90),(x,-40)])).geoms]
tris=[list(t.exterior.coords)[:-1]for p in parts for t in shapely.constrained_delaunay_triangles(p).geoms];D.update(ring=ring,triangles=tris,facePlane=[a,b,k],area=pol.area,uncertainties=['Return face batter0.2m/m is inferred; scan face missing.','Return1m cap width follows narrow LiDAR plateau, exact edges remain uncertain.','Short cap extent follows OSM838550868.'])
(R/'reports/R565_WALL_DESIGN.json').write_text(json.dumps(D,indent=2));print(pol.area,len(tris))
