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

for u in [.1,.3,.5,.7,.9]:
 p=(1-u)*q[3]+u*q[2]
 print('PROFILE',u,[(round(float(a),2),round(hit(p-n*a)[2],3)) for a in np.arange(-2,.51,.1)])

