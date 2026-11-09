from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]

parts=[('triangle_clear',[(400,1100),(550,1020),(610,1100),(460,1200)]),('north_clear',[(800,600),(850,510),(880,530),(830,620)])]
for name,pixels in parts:
 if len(pixels)==3:pixels=[pixels[0],pixels[1],pixels[2],pixels[2]]
 p=np.array([[150+x*.1875,300-y*.1875] for x,y in pixels]);origin=p.mean(axis=0);samples=[]
 for a in np.linspace(.15,.85,25):
  for b in np.linspace(.15,.85,25):
   xy=(1-a)*(1-b)*p[0]+a*(1-b)*p[1]+a*b*p[2]+(1-a)*b*p[-1];h,n,*_=g.ray_cast(Vector((*xy,200)),Vector((0,0,-1)),300)
   if h and n.z>.7 and 5<h.z<120:samples.append([*(xy-origin),h.z])
 arr=np.array(samples);train=arr[::2];test=arr[1::2];A=np.c_[train[:,:2],np.ones(len(train))];mask=np.ones(len(train),bool)
 for _ in range(5):
  fit=np.linalg.lstsq(A[mask],train[mask,2],rcond=None)[0];err=abs(A@fit-train[:,2]);mask=err<max(.12,float(np.percentile(err,65)))
 e=abs(np.c_[test[:,:2],np.ones(len(test))]@fit-test[:,2]);rows.append(dict(name=name,polygon=p.tolist(),origin=origin.tolist(),plane=fit.tolist(),cornerRoofs=[float(np.dot([*(xy-origin),1],fit)) for xy in p],samples=len(arr),support=float(np.mean(e<.25)),p90=float(np.percentile(e,90))))
(R/'config/r279_clear_roof_planes.json').write_text(json.dumps(rows,indent=2));print(rows,flush=True)
