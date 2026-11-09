import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rows=[]
for y in [31,32,33,34,35,36,37,38,39]:
 row=[]
 for j in range(5):
  x=y-66.6+j*.4;h,p,*_=s.ray_cast(dg,Vector((x,y,20)),Vector((0,0,-1)),distance=50);row.append([round(x,2),round(p.z,3) if h else None])
 rows.append({'y':y,'xz':row})
(R/'reports/R490_CORRIDOR_FLOOR.json').write_text(json.dumps(rows,indent=2));print(rows)
