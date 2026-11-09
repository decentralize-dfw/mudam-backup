from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]
for y in [-184,-188,-192,-196,-200,-204]:
 row=[]
 for x in range(-242,-212,2):
  h,n,*_=g.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),300)
  row.append([x,round(h.z,3) if h else None,round(n.z,2) if n else None])
 rows.append(dict(y=y,points=row))
(R/'reports/R240_RUIN_GROUND_SECTIONS.json').write_text(json.dumps(rows,indent=2));print(rows)
