from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R198_KALE_BATI_KALINTI_v001.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 inv=o.matrix_world.inverted(); hits=[]
 for x,y in [(-230,-191),(-226,-193),(-233,-187)]:
  h,p,n,i=o.ray_cast(inv@Vector((x,y,30)),inv.to_3x3()@Vector((0,0,-1)))
  if h:hits.append([x,y,(o.matrix_world@p).z])
 if hits:rows.append(dict(name=o.name,hits=hits))
(R/'reports/R198_INTERSECTING_LAYERS.json').write_text(json.dumps(rows,indent=2))
