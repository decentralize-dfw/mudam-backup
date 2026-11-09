from pathlib import Path
import json,bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=json.loads((R/'config/r191_courtyard_domains.json').read_text());rng=np.random.default_rng(191)
for row in rows:
 samples=[]
 for tri in row['triangles'][::3]:
  x,y=np.mean(tri,axis=0);h,n,*_=bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
  if h and n.z>.9 and h.z<15:samples.append([x,y,h.z])
 a=np.array(samples);origin=a[:,:2].mean(0);X=np.c_[a[:,:2]-origin,np.ones(len(a))];best=None
 for i in range(200):
  ix=rng.choice(len(a),3,replace=False)
  if abs(np.linalg.det(X[ix]))<.01:continue
  c=np.linalg.solve(X[ix],a[ix,2]);mask=abs(X@c-a[:,2])<.2
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(X[best],a[best,2],rcond=None)[0];err=abs(X@c-a[:,2]);row.update(origin=origin.tolist(),plane=c.tolist(),samples=samples,support=float((err<.3).mean()),p90=float(np.quantile(err,.9)))
(R/'config/r191_measured_courts.json').write_text(json.dumps(rows,indent=2));print([(r['name'],r['support'],r['p90'],r['plane']) for r in rows])
