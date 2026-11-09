from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
src=BVHTree.FromPolygons(vs,fs,all_triangles=True)
pixels=[(210,1470),(812,1092),(666,935),(605,907),(560,926)]
p=np.array([[150+x*.1875,300-y*.1875] for x,y in pixels]);c=p.mean(axis=0);rows=[]
for i,a in enumerate(p):
 b=p[(i+1)%len(p)]
 for u in np.linspace(.08,.92,30):
  for v in np.linspace(.1,.9,15):
   xy=c*(1-v)+(a*(1-u)+b*u)*v;h,n,*_=src.ray_cast(Vector((*xy,150)),Vector((0,0,-1)),200)
   if h and n.z>.7:rows.append([*(xy-c),h.z])
arr=np.array(rows);train=arr[::2];test=arr[1::2];A=np.c_[train[:,:2],np.ones(len(train))];mask=np.ones(len(train),bool)
for _ in range(8):
 fit=np.linalg.lstsq(A[mask],train[mask,2],rcond=None)[0];e=abs(A@fit-train[:,2]);mask=e<max(.12,float(np.percentile(e,60)))
e=abs(np.c_[test[:,:2],np.ones(len(test))]@fit-test[:,2])
d=dict(source='R277_east_source_top.png',pixels=pixels,polygon=p.tolist(),origin=c.tolist(),plane=fit.tolist(),samples=len(arr),support=float(np.mean(e<.25)),p90=float(np.percentile(e,90)),maximum=float(max(e)))
(R/'config/r290_south_roof.json').write_text(json.dumps(d,indent=2));print(d,flush=True)
