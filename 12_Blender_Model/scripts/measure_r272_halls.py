from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]

parts=json.loads((R/'config/r233_courtyard_roof_planes.json').read_text())['parts'];u=np.array([.7562829027,.6542447333]);out=[]
for shift in [-48.4,48.4]:
 for part in [0,2]:
  p=np.array(parts[part]['polygon'])+u*shift;origin=p.mean(axis=0);samples=[]
  for a in np.linspace(.1,.9,25):
   for b in np.linspace(.1,.9,25):
    xy=p[0]+a*(p[1]-p[0])+b*(p[3]-p[0]);h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
    if h and n.z>.8 and 5<h.z<8.5:samples.append([*(xy-origin),h.z])
  arr=np.array(samples);train=arr[::2];test=arr[1::2];A=np.c_[train[:,:2],np.ones(len(train))];mask=np.ones(len(train),bool)
  for _ in range(5):
   fit=np.linalg.lstsq(A[mask],train[mask,2],rcond=None)[0];err=abs(A@fit-train[:,2]);mask=err<max(.12,float(np.percentile(err,65)))
  e=abs(np.c_[test[:,:2],np.ones(len(test))]@fit-test[:,2]);out.append(dict(shift=shift,part=part,polygon=p.tolist(),origin=origin.tolist(),plane=fit.tolist(),cornerRoofs=[float(np.dot([*(xy-origin),1],fit)) for xy in p],samples=len(arr),support=float(np.mean(e<.25)),p90=float(np.percentile(e,90))))
(R/'config/r272_court_halls.json').write_text(json.dumps(out,indent=2));print(out,flush=True)
