import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for i in range(49):
 y=18+i*.5
 for j in range(19):
  u=-73.5+j*.25;x=y+u;h,p,n,*_=bpy.context.scene.ray_cast(dg,Vector((x,y,15)),Vector((0,0,-1)),distance=40)
  if h:rows.append(dict(x=x,y=y,u=u,z=p.z,normal=list(n)))
(R/'reports/R510_NW_CAP_SOURCE_GRID.json').write_text(json.dumps(rows,indent=2))
