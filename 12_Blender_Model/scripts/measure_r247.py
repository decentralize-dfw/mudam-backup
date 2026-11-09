from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
p=np.array([[121.75,420.05],[129.7,426.5],[136.85,417.8],[128.85,411.2]])
rows=[]
for a in [.03,.1,.5,.9,.97]:
 for b in [.03,.1,.5,.9,.97]:
  xy=p[0]+a*(p[1]-p[0])+b*(p[3]-p[0]);h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
  if h:rows.append(dict(a=a,b=b,xy=xy.tolist(),z=h.z,nz=n.z))
(R/'config/r247_hall_edge_measurements.json').write_text(json.dumps(rows,indent=2));print(rows)
