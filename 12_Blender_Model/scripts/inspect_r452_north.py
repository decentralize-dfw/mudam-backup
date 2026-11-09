import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R451_KALE_BURC_YUZEY_NORMALLERI_ADAY_v001.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.hide_set(o.hide_render)
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();out=[]
for px,py in [(500,275),(650,275),(750,275),(750,245),(750,300),(610,300),(550,350),(930,260),(1040,280),(600,620)]:
 hits=[];z=150
 for i in range(7):
  hit,loc,n,idx,o,m=bpy.context.scene.ray_cast(dep,Vector((-120+px*220/1400,95-py*220/1400,z)),Vector((0,0,-1)))
  if not hit:break
  hits.append(dict(name=o.name,z=loc.z));z=loc.z-.01
 out.append(dict(pixel=[px,py],hits=hits))
(R/'reports/R452_NORTH_SURFACE_RAYS.json').write_text(json.dumps(out,indent=2))
