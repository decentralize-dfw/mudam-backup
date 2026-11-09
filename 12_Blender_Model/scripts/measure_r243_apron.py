from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'))
t=Vector((-229.6,-192.1,-18));cam=t+Vector((35,-45,45));rot=(t-cam).to_track_quat('-Z','Y');vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in tr.vertices] for tr in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
pixels=[(340,245),(610,140),(675,295),(797,590),(635,610),(585,310),(360,320)]
pts=[];normals=[]
for x,y in pixels:
 origin=cam+rot@Vector(((x/1000-.5)*48,(.5-y/850)*48*850/1000,0));h,n,_,_=g.ray_cast(origin,rot@Vector((0,0,-1)),300)
 assert h is not None
 pts.append(list(h));normals.append(list(n))
from mathutils.geometry import tessellate_polygon
flat=[Vector((p[0],p[1],0)) for p in pts];tri=tessellate_polygon([flat]);ids=[list(t) if isinstance(t[0],int) else [flat.index(v) for v in t] for t in tri]
errors=[];samples=[]
for ids3 in ids:
 a,b,c=[Vector(pts[k]) for k in ids3]
 for i in range(1,9):
  for j in range(1,9-i):
   p=a+(b-a)*i/9+(c-a)*j/9;h,n,*_=g.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),300)
   if h is not None and n.z>.85:errors.append(abs(p.z-h.z));samples.append([h.x,h.y,h.z])
import numpy as np
arr=np.array(samples);origin=arr[:,:2].mean(axis=0);x,y=((arr[:,:2]-origin)/20).T;A=np.column_stack([np.ones(len(arr)),x,y,x*x,x*y,y*y]);train=np.arange(len(arr))%2==0;mask=train.copy()
for _ in range(5):
 fit=np.linalg.lstsq(A[mask],arr[mask,2],rcond=None)[0];res=abs(A@fit-arr[:,2]);mask=train&(res<max(.15,np.percentile(res[train],75)))
held=abs(A[~train]@fit-arr[~train,2])
d=dict(gradeOrigin=origin.tolist(),gradeScale=20,gradeCoefficients=fit.tolist(),gradeHeldoutP90=float(np.percentile(held,90)),gradeSupport=float(np.mean(held<.35)),pixels=pixels,points=pts,normals=normals,triangles=ids,checks=len(errors),p90=float(np.percentile(errors,90)),maximum=max(errors),accepted=False,source='R239_ruin_source.png',method='Source-traced apron corners, independent triangular architectural grades; not source mesh copying')
(R/'config/r243_uphill_apron.json').write_text(json.dumps(d,indent=2));print(d)
