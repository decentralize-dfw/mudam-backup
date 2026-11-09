from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
pixels=[(255,642),(1065,468),(1140,733),(325,907)];q=np.array([[-80+(x-700)/25,-301+(700-y)/25] for x,y in pixels]);nx=221;ny=81;t=q[1]-q[0];t/=np.linalg.norm(t);n=np.array([-t[1],t[0]]);rears=[];fronts=[];offsets=[]
def hit(p):
 h,*_=tree.ray_cast(Vector((float(p[0]),float(p[1]),40)),Vector((0,0,-1)),200);assert h;return list(h)
for u in np.linspace(0,1,nx):
 p=(1-u)*q[0]+u*q[1];last=-2.0
 for step in np.arange(-2,4.51,.05):
  h=hit(p+n*step)
  if h[2]<-66.0:break
  last=float(step)
 offsets.append(last);rears.append(p+n*last)
 p=(1-u)*q[3]+u*q[2];last=-2.0
 for step in np.arange(-2,.51,.025):
  h=hit(p-n*step)
  if h[2]<-66.0:break
  last=float(step)
 fronts.append(p-n*last)
v=[]
for vv in np.linspace(0,1,ny):
 for i,u in enumerate(np.linspace(0,1,nx)):
  front=fronts[i];v.append(hit((1-vv)*rears[i]+vv*front))
(D/'row_whole_roof_samples_v061.json').write_text(json.dumps(dict(vertices=v,nx=nx,ny=ny,ring=q.tolist(),pixels=pixels,rear_offsets=offsets,source_rule='Whole four-house contiguous row, roof edge traced in registered top view. Rear extension last continuous source z>=-66; search4.5m. Manual trace is approximate.')))
print('FULL_ROW',len(v),min(p[2] for p in v),max(p[2] for p in v),'capped',sum(x>=4.5 for x in offsets))

