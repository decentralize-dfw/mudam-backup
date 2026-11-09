import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'reports/R549_GAP_FOOTPRINT.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get()
for part in d:
 rows=[]
 for x,y in part['samples']:
  h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,30)),Vector((0,0,-1)),distance=60)
  if h:rows.append([x,y,p.z])
 part['controls']=rows
(R/'reports/R549_GAP_CONTROLS.json').write_text(json.dumps(d))
