import json,sys,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,LineString,box
from shapely.ops import split
from shapely import constrained_delaunay_triangles
rows=json.loads((R/'reports/R551_NORTH_GRADE_FACE_CONTROLS.json').read_text());q=np.array([[r['x'],r['z'],r['y']]for r in rows if r['x']>=-20 and -7<r['z']<-5.2]);A=np.c_[q[:,:2],np.ones(len(q))];tr=np.arange(len(q))%4!=0;face=np.linalg.lstsq(A[tr],q[tr,2],rcond=None)[0];err=A[~tr]@face-q[~tr,2];c=json.loads((R/'reports/R548_SLOPE_PLANES.json').read_text())['coefficients'];a,b,k=face
# Solve the intersection of independently fitted sloping cap and battered face.
def front(x):return (a*x+b*(c[0]*x+c[2]+c[3]*max(x+20,0)+c[4]*max(x+16,0))+k)/(1-b*c[1])
xs=[-27.25,-20,-16,-12.8];poly=Polygon([(x,front(x))for x in xs]+[(-12.8,4.0),(-27.25,4.0)]);terr=Polygon(json.loads((R/'reports/R523_WEST_REBUILD_DOMAINS.json').read_text())['terraceOutline']);poly=poly.difference(terr);parts=[poly]
for x in (-20,-16):parts=[g for p in parts for g in split(p,LineString([(x,-3),(x,8)])).geoms]
tris=[list(t.exterior.coords)[:3]for p in parts for t in constrained_delaunay_triangles(p).geoms];d=dict(triangles=tris,capCoefficients=c,faceYfromXZ=face.tolist(),area=poly.area,faceHeldout=dict(count=int(sum(~tr)),rms=float(np.sqrt(np.mean(err*err))),max=float(max(abs(err)))),method='Independent sloping masonry plinth: source R551 close photograph-like reference view confirms stone face and rising cap. Face measured central visible band; extension west is an architectural plane assumption, not fully verified. Cap R548 independent planes.');(R/'reports/R552_SLOPING_MASONRY_DESIGN.json').write_text(json.dumps(d,indent=2));print(poly.area,d['faceHeldout'])
