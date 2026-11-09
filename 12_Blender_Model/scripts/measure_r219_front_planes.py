from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]
for r in json.loads((R/'config/r218_front_volumes_measured.json').read_text())['parts']:
 if r['supported']:continue
 p=np.array(r['polygon']);origin=p.mean(axis=0);samples=[]
 for a in np.linspace(.15,.85,15):
  for b in np.linspace(.15,.85,15):
   xy=p[0]+a*(p[1]-p[0])+b*(p[3]-p[0]);h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
   if h and n.z>.85 and 6<h.z<10:samples.append([*(xy-origin),float(h.z)])
 arr=np.array(samples);train=arr[::2];test=arr[1::2];A=np.column_stack([train[:,:2],np.ones(len(train))]);mask=np.ones(len(train),dtype=bool)
 for _ in range(4):
  fit=np.linalg.lstsq(A[mask],train[mask,2],rcond=None)[0];mask=abs(A@fit-train[:,2])<.20
 err=abs(np.column_stack([test[:,:2],np.ones(len(test))])@fit-test[:,2]);support=float(np.mean(err<.2));p90=float(np.percentile(err,90));corners=[float(np.dot([*(xy-origin),1],fit))for xy in p]
 rows.append(dict(id=r['id'],polygon=p.tolist(),origin=origin.tolist(),plane=fit.tolist(),cornerRoofs=corners,samples=len(arr),heldOutP90=p90,heldOutSupport=support,supported=support>=.9 and p90<=.2))
(R/'config/r219_front_planes.json').write_text(json.dumps(dict(parts=rows,method='Independent single roof plane fitted to alternating source samples; held-out samples reported'),indent=2));print(rows,flush=True)
