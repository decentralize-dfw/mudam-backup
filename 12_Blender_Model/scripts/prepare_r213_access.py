from pathlib import Path
import json,sys,numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon,box,LineString,Point
from shapely.ops import split
rows=json.loads((R/'config/r213_access_measured.json').read_text());rng=np.random.default_rng(213);used=Polygon();white=rows[-1];white_polygon=Polygon(white['xy']);rows=rows[:-1]
# The white forecourt crosses a real level break. Keep two architectural domains
# rather than averaging the upper deck and lower paved approach into one plane.
parts=split(white_polygon,LineString([(-43,351),(12,411)]))
for i,p in enumerate(parts.geoms):
 samples=[a for a in white['measurements'] if p.covers(Point(a[:2]))];a=np.array(samples);origin=a[:,:2].mean(0);X=np.c_[a[:,:2]-origin,np.ones(len(a))];best=None
 for _ in range(500):
  ids=rng.choice(len(a),3,replace=False)
  try:c=np.linalg.solve(X[ids],a[ids,2])
  except np.linalg.LinAlgError:continue
  mask=np.abs(X@c-a[:,2])<.22
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(X[best],a[best,2],rcond=None)[0]
 rows.append(dict(name='SOUTH_CONCRETE_'+str(i),xy=list(p.exterior.coords)[:-1],measurements=samples,origin=origin.tolist(),plane=c.tolist(),support=float(best.mean()),samples=len(a),inliers=int(best.sum()),p90=float(np.quantile(np.abs(X[best]@c-a[best,2]),.9))))
for row in rows:
 a=np.array(row['measurements']);xy=(a[:,:2]-row['origin'])/20;x,y=xy.T;X=np.c_[x,y,np.ones(len(a)),x*x,x*y,y*y];best=None
 for _ in range(1500):
  ids=rng.choice(len(a),6,replace=False)
  try:c=np.linalg.solve(X[ids],a[ids,2])
  except np.linalg.LinAlgError:continue
  mask=np.abs(X@c-a[:,2])<.22
  if best is None or mask.sum()>best.sum():best=mask
 for _ in range(3):
  c=np.linalg.lstsq(X[best],a[best,2],rcond=None)[0];best=np.abs(X@c-a[:,2])<.22
 res=np.abs(X@c-a[:,2]);row['quadratic']=c.tolist();row['quadratic_support']=float(best.mean());row['quadratic_p90']=float(np.quantile(res[best],.9));row['quadratic_all_p90']=float(np.quantile(res,.9))
 p=shapely.make_valid(Polygon(row['xy'])).difference(used)
 if row['name']=='SOUTH_LOOP':p=p.difference(white_polygon)
 used=shapely.union_all([used,p]);tris=[]
 for gx in range(int(p.bounds[0])-1,int(p.bounds[2])+2,2):
  for gy in range(int(p.bounds[1])-1,int(p.bounds[3])+2,2):
   for t in shapely.constrained_delaunay_triangles(p.intersection(box(gx,gy,gx+2,gy+2))).geoms:
    if t.area>1e-8:tris.append(list(t.exterior.coords)[:-1])
 row['triangles']=tris;row['cuts']=[list(t.exterior.coords)[:-1] for t in shapely.constrained_delaunay_triangles(p).geoms if t.area>1e-8];row['area']=p.area
 print(row['name'],row['quadratic_support'],row['quadratic_p90'],row['quadratic_all_p90'],len(tris))
(R/'config/r213_access_surfaces.json').write_text(json.dumps(rows))
