from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]


u=np.array([.7562829027,.6542447333]);out=[]
for offset in [-.2,0,.2,.4,.6,.8]:
 shift=-48.4
 d=json.loads((R/'config/r228_glazed_link_measure.json').read_text());start=np.array(d['start'])+u*shift;end=np.array(d['end'])+u*shift;axis=np.array(d['axis']);trans=np.array(d['trans']);length=d['length'];width=d['width'];start=start+trans*offset;end=end+trans*offset;samples=[]
 for along in np.linspace(.12,.88,21):
  for across in np.linspace(-.4,.4,13):
   xy=start+axis*length*along+trans*width*across;h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
   if h and 2<h.z<14:samples.append([length*along,width*across,h.z])
 arr=np.array(samples);A=np.column_stack([np.ones(len(arr)),arr[:,0],arr[:,1],arr[:,1]**2]);train=np.arange(len(arr))%2==0;fit=np.linalg.lstsq(A[train],arr[train,2],rcond=None)[0];err=abs(A[~train]@fit-arr[~train,2]);out.append(dict(shift=shift,offset=offset,start=start.tolist(),end=end.tolist(),axis=axis.tolist(),trans=trans.tolist(),length=length,width=width,fit=fit.tolist(),samples=len(arr),heldOutP90=float(np.percentile(err,90)),support=float(np.mean(err<.25))))
(R/'config/r270_left_link_candidates.json').write_text(json.dumps(out,indent=2));print(out,flush=True)
