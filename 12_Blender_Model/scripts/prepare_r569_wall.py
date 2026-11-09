from pathlib import Path
import sys,json
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import shapely
from shapely.geometry import Polygon,LineString
from shapely.ops import split
D=json.loads((R/'reports/R569_CONTINUOUS_CAP_PLANES.json').read_text());c=D['coefficients'];a,b,k=json.loads((R/'reports/R529_SOUTH_FACE_PLANE.json').read_text())['plane']
def z(x,y):return c[0]+c[1]*(x-49.5)+c[2]*(y+58)+c[3]*max(x-54,0)+c[4]*max(x-56,0)
def front(x):return(a*x+b*(z(x,0))+k)/(1-b*c[2])
xs=[49.04445,54,56,64,72.13087];ring=[(49.5,-52.53),(49.5,-57.5)]+[(x,front(x))for x in xs]+[(x,front(x)+2)for x in reversed(xs[1:])]+[(50.5,front(50.5)+2),(50.5,-52.53)]
def width(x):return .85+min(2,max(0,x-54))*.5+min(8.13087,max(0,x-64))*.15/8.13087
ring=[(49.5,-52.53),(49.5,-57.5)]+[(x,front(x))for x in xs]+[(x,front(x)+width(x))for x in reversed(xs[1:])]+[(50.5,front(50.5)+width(50.5)),(50.5,-52.53)]
pol=Polygon(ring);assert pol.is_valid;parts=[pol]
for x in [54,56,64]:parts=[q for p in parts for q in split(p,LineString([(x,-90),(x,-40)])).geoms]
tris=[list(t.exterior.coords)[:-1]for p in parts for t in shapely.constrained_delaunay_triangles(p).geoms];D.update(ring=ring,triangles=tris,facePlane=[a,b,k],area=pol.area,uncertainties=['Return face batter0.2m/m is inferred; scan face missing.','Return1m cap width follows narrow LiDAR plateau, exact edges remain uncertain.','Short cap extent follows OSM838550868.'])
(R/'reports/R569_WALL_DESIGN.json').write_text(json.dumps(D,indent=2));print(pol.area,len(tris))

oldfront=lambda x:a*x+b*(-2.02+min(1,max(0,(x-54)/4))*.57)+k
xx=[50.5,54,56,58,64,72,72.13087]
strip=Polygon([(x,front(x)+width(x))for x in xx]+[(x,oldfront(x)+2)for x in reversed(xx)]).buffer(0).difference(Polygon(json.loads((R/'reports/R532_WHOLE_PAVING_PLANES.json').read_text())['outline'])).difference(pol)
parts=list(strip.geoms)if hasattr(strip,'geoms')else[strip]
for x in [58,72]:parts=[q for p in parts for q in split(p,LineString([(x,-90),(x,-40)])).geoms]
D['floorTriangles']=[list(t.exterior.coords)[:-1]for p in parts if p.area>1e-8 for t in shapely.constrained_delaunay_triangles(p).geoms];D['floorArea']=sum(p.area for p in parts);D['uncertainties']=['Return batter inferred; upper return not independently classified as ground.','Cap width bounded between high classified cap and lower classified floor cells,0.25m sampling interval.'];(R/'reports/R569_WALL_DESIGN.json').write_text(json.dumps(D,indent=2));print('floor',D['floorArea'])
