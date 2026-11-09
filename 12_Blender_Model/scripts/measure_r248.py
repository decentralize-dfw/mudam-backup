from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
p=np.array([[126.65,416.45],[132.7,421.4],[134.3,419.45],[128.15,414.5]])
rows=[]
for a in np.linspace(.15,.85,15):
 for b in np.linspace(.35,.9,15):
  xy=p[0]+a*(p[1]-p[0])+b*(p[3]-p[0]);h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
  if h and 6.0<h.z<7.4:rows.append([*xy,h.z])
arr=np.array(rows);A=np.column_stack([arr[:,:2]-p.mean(axis=0),np.ones(len(arr))]);mask=np.ones(len(arr),dtype=bool)
for _ in range(5):
 fit=np.linalg.lstsq(A[mask][::2],arr[mask][::2,2],rcond=None)[0];err=abs(A@fit-arr[:,2]);mask=err<.2
print('FIT',fit,'support',np.mean(mask),'p90',np.percentile(err,90),flush=True)
(R/'config/r248_second_light_fit.json').write_text(json.dumps(dict(plane=fit.tolist(),origin=p.mean(axis=0).tolist(),support=float(np.mean(mask)),p90=float(np.percentile(err,90)),samples=len(arr)),indent=2))
