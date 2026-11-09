import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for x,y in json.loads((R/'reports/R548_SLOPE_SAMPLES.json').read_text()):
 h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,30)),Vector((0,0,-1)),distance=60)
 if h:rows.append([x,y,p.z])
(R/'reports/R548_SLOPE_CONTROLS.json').write_text(json.dumps(rows))
