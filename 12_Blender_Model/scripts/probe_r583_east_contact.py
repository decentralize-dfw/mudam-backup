import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R580_KALE_DUVAR_KAPALI_KABUK_ADAY_v001.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for x in [44,46,48,50,52,54]:
 for y in [25,20,15,10,5,0,-5,-10,-15,-20,-25]:
  start=Vector((x,y,4));hits=[]
  for i in range(4):
   h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,start,Vector((0,0,-1)),distance=25)
   if not h:break
   hits.append([o.name,round(p.z,4)]);start=p-Vector((0,0,.002))
  rows.append(dict(x=x,y=y,hits=hits))
(R/'reports/R583_EAST_CONTACT_PROBES.json').write_text(json.dumps(rows,indent=2));print(rows)
