from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]

# Reference top-view bounds of the curved glazed connection, not extracted mesh.
pixels=[(728,674),(753,708),(903,586),(879,553)]
p=np.array([[92.5+.05*x,446.5-.05*y]for x,y in pixels]);start=(p[0]+p[1])/2;end=(p[2]+p[3])/2;axis=end-start;length=np.linalg.norm(axis);axis/=length;trans=np.array([-axis[1],axis[0]]);width=(np.linalg.norm(p[1]-p[0])+np.linalg.norm(p[2]-p[3]))/2;samples=[]
for along in np.linspace(.12,.88,21):
 for across in np.linspace(-.4,.4,13):
  xy=start+axis*length*along+trans*width*across;h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
  if h and 2<h.z<14:samples.append([length*along,width*across,h.z])
a=np.array(samples);A=np.column_stack([np.ones(len(a)),a[:,0],a[:,1],a[:,1]**2]);train=np.arange(len(a))%2==0;fit=np.linalg.lstsq(A[train],a[train,2],rcond=None)[0];err=abs(A[~train]@fit-a[~train,2]);result=dict(pixels=pixels,start=start.tolist(),end=end.tolist(),axis=axis.tolist(),trans=trans.tolist(),length=float(length),width=float(width),fit=fit.tolist(),samples=len(a),heldOutP90=float(np.percentile(err,90)),support=float(np.mean(err<.25)),limits='Independent analytic barrel approximation from scalar source measurements; footprint visually traced, no mesh copied')
(R/'config/r231_cross_link_measure.json').write_text(json.dumps(result,indent=2));print(result,flush=True)

