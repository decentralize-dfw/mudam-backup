from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();out=[]
for x in range(260,341,10):
 for y in range(425,496,10):
  hit,h,n,*_=bpy.context.scene.ray_cast(dg,Vector((x,y,150)),Vector((0,0,-1)),distance=250)
  if hit and n.z>.9 and h.z<28:out.append([x,y,h.z])
print(out);(R/'reports/R176_MAMA_EXTERIOR_LEVELS.json').write_text(json.dumps(out,indent=2))
