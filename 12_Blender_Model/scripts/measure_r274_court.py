from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]

parts=[('left_vegetated',[(70,400),(460,65),(830,449),(510,710)]),('left_edge',[(540,750),(870,485),(904,521),(574,786)])]
for name,pixels in parts:
 p=np.array([[82.7+x/60,397.2-y/60] for x,y in pixels]);origin=p.mean(axis=0);samples=[]
 for a in np.linspace(.15,.85,25):
  for b in np.linspace(.15,.85,25):
   xy=p[0]+a*(p[1]-p[0])+b*(p[3]-p[0]);h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
   if h and n.z>.7 and 3<h.z<9:samples.append([*(xy-origin),h.z])
 arr=np.array(samples);train=arr[::2];test=arr[1::2];A=np.c_[train[:,:2],np.ones(len(train))];mask=np.ones(len(train),bool)
 for _ in range(5):
  fit=np.linalg.lstsq(A[mask],train[mask,2],rcond=None)[0];err=abs(A@fit-train[:,2]);mask=err<max(.12,float(np.percentile(err,65)))
 e=abs(np.c_[test[:,:2],np.ones(len(test))]@fit-test[:,2]);rows.append(dict(name=name,polygon=p.tolist(),origin=origin.tolist(),plane=fit.tolist(),cornerRoofs=[float(np.dot([*(xy-origin),1],fit)) for xy in p],samples=len(arr),support=float(np.mean(e<.25)),p90=float(np.percentile(e,90))))
(R/'config/r274_left_court_planes.json').write_text(json.dumps(rows,indent=2));print(rows,flush=True)
