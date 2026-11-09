from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]

parts=[('right_light_1',[(270,560),(610,280),(715,409),(375,689)]),('right_light_2',[(415,729),(751,451),(854,570),(518,848)]),('right_membrane',[(590,881),(865,650),(899,690),(624,921)]),('right_back',[(100,400),(437,111),(541,237),(204,526)])]
for name,pixels in parts:
 p=np.array([[155.9+x/60,460.55-y/60] for x,y in pixels]);origin=p.mean(axis=0);samples=[]
 for a in np.linspace(.15,.85,25):
  for b in np.linspace(.15,.85,25):
   xy=p[0]+a*(p[1]-p[0])+b*(p[3]-p[0]);h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
   if h and n.z>.7 and 3<h.z<9:samples.append([*(xy-origin),h.z])
 arr=np.array(samples);train=arr[::2];test=arr[1::2];A=np.c_[train[:,:2],np.ones(len(train))];mask=np.ones(len(train),bool)
 for _ in range(5):
  fit=np.linalg.lstsq(A[mask],train[mask,2],rcond=None)[0];err=abs(A@fit-train[:,2]);mask=err<max(.12,float(np.percentile(err,65)))
 e=abs(np.c_[test[:,:2],np.ones(len(test))]@fit-test[:,2]);rows.append(dict(name=name,polygon=p.tolist(),origin=origin.tolist(),plane=fit.tolist(),cornerRoofs=[float(np.dot([*(xy-origin),1],fit)) for xy in p],samples=len(arr),support=float(np.mean(e<.25)),p90=float(np.percentile(e,90))))
(R/'config/r273_right_court_planes.json').write_text(json.dumps(rows,indent=2));print(rows,flush=True)
