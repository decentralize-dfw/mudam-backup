from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
domains=[('WEST_INNER_GROUND',[(500,600),(647,537),(735,657),(694,696),(615,682)]),('NORTH_INNER_GROUND',[(809,474),(912,426),(920,531),(850,543)]),('TRIANGLE_INNER_GROUND',[(900,650),(1010,641),(1011,752),(959,720)])]
def inside(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
out=[];rng=np.random.default_rng(172)
for name,pixels in domains:
 xy=[[-340+x*260/1600,-45-y*260/1600] for x,y in pixels];samples=[]
 for x in np.linspace(min(p[0] for p in xy),max(p[0] for p in xy),15)[1:-1]:
  for y in np.linspace(min(p[1] for p in xy),max(p[1] for p in xy),15)[1:-1]:
   if not inside((x,y),xy):continue
   h,n,*_=bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),300)
   if h and abs(n.z)>.85:samples.append([x,y,h.z])
 a=np.array(samples);origin=a[:,:2].mean(0);X=np.c_[a[:,:2]-origin,np.ones(len(a))];best=None
 for i in range(300):
  ix=rng.choice(len(a),3,replace=False)
  if abs(np.linalg.det(X[ix]))<.01:continue
  c=np.linalg.solve(X[ix],a[ix,2]);mask=abs(X@c-a[:,2])<.25
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(X[best],a[best,2],rcond=None)[0];err=abs(X@c-a[:,2]);support=float((err<.3).mean());out.append(dict(name=name,xy=xy,pixels=pixels,origin=origin.tolist(),plane=c.tolist(),samples=samples,support=support,p90=float(np.quantile(err,.9)),accepted=bool(support>.85 and np.linalg.norm(c[:2])<.35)))
(R/'reports/R172_PLATFORM_FITS_v011.json').write_text(json.dumps(out,indent=2));print([(r['name'],r['support'],r['p90'],r['accepted']) for r in out])

