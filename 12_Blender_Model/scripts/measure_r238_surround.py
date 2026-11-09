from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);poly=[(-237.625,-186.2125),(-238.6,-196.2875),(-226.25,-202.625),(-215.3625,-194.5)]
from mathutils.geometry import tessellate_polygon
tri=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]])
ruin=json.loads((R/'reports/R198_RUIN_MEASUREMENTS.json').read_text())['xy']
def inside(p):
 signs=[(b[0]-a[0])*(p.y-a[1])-(b[1]-a[1])*(p.x-a[0]) for a,b in zip(ruin,ruin[1:]+ruin[:1])]
 return min(signs)>=0 or max(signs)<=0
samples=[]
for ids in tri:
 t=[Vector((*poly[k],0)) for k in ids] if isinstance(ids[0],int) else ids
 for i in range(1,17):
  for j in range(1,17-i):
   p=t[0]+(t[1]-t[0])*i/17+(t[2]-t[0])*j/17
   if inside(p):continue
   hit,n,*_=g.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),300)
   if hit is not None and n.z>.9 and -26<hit.z<-16:samples.append([p.x,p.y,hit.z])
a=np.array(samples);origin=np.mean(a[:,:2],axis=0);A=np.column_stack([a[:,:2]-origin,np.ones(len(a))]);train=np.arange(len(a))%2==0;mask=train.copy()
for _ in range(5):
 fit=np.linalg.lstsq(A[mask],a[mask,2],rcond=None)[0];e=abs(A@fit-a[:,2]);mask=train&(e<max(.2,np.percentile(e[train],70)))
e=abs(A[~train]@fit-a[~train,2]);d=dict(polygon=poly,origin=origin.tolist(),plane=fit.tolist(),samples=len(a),p90=float(np.percentile(e,90)),support=float(np.mean(e<.35)),accepted=False)
(R/'config/r238_ruin_surround_grade.json').write_text(json.dumps(d,indent=2));print(d)

