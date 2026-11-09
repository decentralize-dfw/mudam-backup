import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R460_KUZEY_AVLU_GECIS_ADAY_v001.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.hide_set(o.hide_render)
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();out=[]
for px,py in [(610,450),(550,520),(470,400)]:
 hits=[];z=150
 for i in range(7):
  hit,loc,n,idx,o,m=bpy.context.scene.ray_cast(dep,Vector((-65.5+px*.035,54.5-py*.035,z)),Vector((0,0,-1)))
  if not hit:break
  hits.append(dict(name=o.name,z=loc.z));z=loc.z-.01
 out.append(dict(pixel=[px,py],hits=hits))
(R/'reports/R462_EXISTING_GLAZING_AREA.json').write_text(json.dumps(out,indent=2))
