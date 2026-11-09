from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]
for name,aa,bb in [('south_road',(189.375,24.375),(255,126.375)),('north_road',(255,126.375),(335,250))]:
 a=np.array(aa);b=np.array(bb);L=np.linalg.norm(b-a);u=(b-a)/L;n=np.array([-u[1],u[0]]);samples=[]
 for s in np.arange(2,L-2,2):
  for z in np.arange(13,23,.5):
   p=a+u*s+n*12;h,no,*_=g.ray_cast(Vector((*p,z)),Vector((*(-n),0)),24)
   if h is not None and abs(no.x*n[0]+no.y*n[1])>.65:
    depth=np.dot(np.array(h[:2])-a-u*s,n)
    if abs(depth)<8:samples.append([s,z,float(depth)])
 pts=np.array(samples);X=np.c_[pts[:,0]/L,pts[:,1]-18,np.ones(len(pts))];rng=np.random.default_rng(306);best=None
 for _ in range(500):
  ix=rng.choice(len(pts),3,replace=False)
  if abs(np.linalg.det(X[ix]))<.01:continue
  fit=np.linalg.solve(X[ix],pts[ix,2]);mask=abs(X@fit-pts[:,2])<.15
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(X[best],pts[best,2],rcond=None)[0];e=abs(X@c-pts[:,2]);rows.append(dict(name=name,a=aa,b=bb,u=u.tolist(),normal=n.tolist(),length=L,coefficients=c.tolist(),samples=samples,inliers=int((e<.25).sum()),support=float((e<.25).mean()),p90=float(np.quantile(e,.9)),inlierP90=float(np.quantile(e[e<.25],.9))))
(R/'config/r306_podium_facade_planes.json').write_text(json.dumps(rows,indent=2));print([{k:v for k,v in r.items() if k!='samples'} for r in rows])
