import sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from shapely.geometry import Polygon
from shapely import constrained_delaunay_triangles
d=json.loads((R/'reports/R534_RUIN_WALL_DESIGN.json').read_text());line=np.array(d['stations'])[:,:2];inside=[]
for i,p in enumerate(line):
 t=line[min(i+1,len(line)-1)]-line[max(0,i-1)];t/=np.linalg.norm(t);inside.append((p-np.array([-t[1],t[0]])*.325).tolist())
platform=json.loads((R/'reports/R328_RUIN_FLOOR_PLANES.json').read_text())['east']['outline'];poly=Polygon(inside+[platform[2],platform[1],platform[0]]);assert poly.is_valid
data=json.loads((R/'reports/R535_MOAT_GROUND.json').read_text());q=np.array(data['0']['controls']+data['5']['controls']);A=np.c_[q[:,:2],np.ones(len(q))];keys=np.floor(q[:,:2]/.4).astype(int);test=(keys[:,0]+keys[:,1]*3)%4==0;c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];e=A[test]@c-q[test,2]
out=dict(outline=list(poly.exterior.coords)[:-1],triangles=[list(t.exterior.coords)[:3]for t in constrained_delaunay_triangles(poly).geoms],plane=c.tolist(),controls=q.tolist(),heldout=dict(count=int(sum(test)),rms=float(np.sqrt(np.mean(e*e))),max=float(max(abs(e)))),accepted=False)
(R/'reports/R536_EAST_MOAT_DESIGN.json').write_text(json.dumps(out,indent=2));print(poly.area,out['heldout'])
