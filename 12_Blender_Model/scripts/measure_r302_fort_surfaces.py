import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def inside(p,ring):
 c=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:c=not c
 return c
def xy(p):return [-305+p[0]*300/1400,25-p[1]*300/1400]
rows=[]
for name,pixels in [('NORTH_COURT',[(405,669),(556,608),(554,699),(592,696),(597,747),(471,763)]),('EAST_UPPER_TERRACE',[(765,575),(880,520),(971,418),(1124,519),(1002,601),(971,643),(895,683)])]:
 ring=[xy(p) for p in pixels];samples=[]
 for x in np.arange(min(p[0] for p in ring)+.33,max(p[0] for p in ring),1.1):
  for y in np.arange(min(p[1] for p in ring)+.41,max(p[1] for p in ring),1.1):
   if not inside((x,y),ring):continue
   h,n,*_=bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),300)
   if h and abs(n.z)>.9:samples.append([x,y,h.z])
 a=np.array(samples);origin=a[:,:2].mean(0);X=np.c_[a[:,:2]-origin,np.ones(len(a))];rng=np.random.default_rng(302);best=None
 for _ in range(500):
  ix=rng.choice(len(a),3,replace=False)
  if abs(np.linalg.det(X[ix]))<.01:continue
  c=np.linalg.solve(X[ix],a[ix,2]);mask=abs(X@c-a[:,2])<.25
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(X[best],a[best,2],rcond=None)[0];err=abs(X@c-a[:,2]);rows.append(dict(name=name,pixels=pixels,xy=ring,origin=origin.tolist(),plane=c.tolist(),samples=len(a),support=float((err<.3).mean()),p90=float(np.quantile(err,.9)),source='Matched orthographic ACT reference; independent planar architectural surface; no source faces transferred'))
outer=[xy(p) for p in [(672,575),(791,532),(871,489),(966,389),(1127,524),(1052,574),(1003,638),(949,704),(884,775)]]
heights=[]
for x,y in outer:
 zs=[]
 for dx,dy in [(0,0),(.4,0),(-.4,0),(0,.4),(0,-.4)]:
  h,n,*_=bvh.ray_cast(Vector((x+dx,y+dy,100)),Vector((0,0,-1)),300)
  if h:zs.append(h.z)
 heights.append(float(np.median(zs)) if zs else None)
(R/'config/r302_fort_surfaces.json').write_text(json.dumps(dict(rows=rows,eastOuter=outer,eastOuterHeights=heights),indent=2));print(rows,heights,flush=True)
