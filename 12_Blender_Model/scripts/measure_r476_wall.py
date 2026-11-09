import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rows=[]
for y in [21,24,27,30,33,36,39,42]:
 row=[]
 for i in range(25):
  x=1.4*y-84+i*.3-2;hit,loc,*rest=s.ray_cast(dg,Vector((x,y,30)),Vector((0,0,-1)),distance=60);row.append([round(x,2),round(loc.z,3) if hit else None])
 rows.append({'y':y,'xz':row})
(R/'reports/R476_WALL_CROSS_SECTIONS.json').write_text(json.dumps(rows,indent=2));print(rows)
