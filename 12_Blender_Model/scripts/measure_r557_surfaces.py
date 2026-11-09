import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'reports/R557_GAP_DOMAINS.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get()
for q in d:
 rows=[]
 for x,y in q['samples']:
  h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1)),distance=80)
  if h:rows.append([x,y,p.z])
 q['sourceControls']=rows
(R/'reports/R557_SOURCE_CONTROLS.json').write_text(json.dumps(d,indent=2))
