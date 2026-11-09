import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for x in [15,25,35,45,55]:
 row=[]
 for i in range(25):
  y=.32*x-66+(i-12)*.3;h,p,*_=bpy.context.scene.ray_cast(dg,Vector((x,y,20)),Vector((0,0,-1)),distance=50);row.append([round(y,2),round(p.z,3) if h else None])
 rows.append(dict(x=x,yz=row))
(R/'reports/R494_FRONT_WALL_SECTIONS.json').write_text(json.dumps(rows,indent=2));print(rows)
