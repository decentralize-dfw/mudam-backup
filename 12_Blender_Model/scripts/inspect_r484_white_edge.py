import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R484_KUZEYBATI_ISTINAT_DUVARI_ADAY_v002.blend'));s=bpy.context.scene
# Respect render visibility during diagnostic ray casting.
for o in s.objects:
 if o.hide_render:o.hide_set(True)
bpy.ops.object.camera_add(location=(-80,0,35));cam=bpy.context.object;cam.rotation_euler=(Vector((-48,37,-5))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();right=cam.matrix_world.to_3x3()@Vector((1,0,0));up=cam.matrix_world.to_3x3()@Vector((0,1,0));forward=cam.matrix_world.to_3x3()@Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get();out=[]
for px,py in [(448,550),(500,570),(550,587),(640,548),(690,532)]:
 origin=cam.location+right*((px/1000-.5)*43)+up*((.5-py/1000)*43);h,loc,n,i,o,mat=s.ray_cast(dg,origin,forward,distance=200);out.append(dict(pixel=[px,py],object=o.name if h else None,position=list(loc) if h else None))
(R/'reports/R484_WHITE_EDGE_RAYS.json').write_text(json.dumps(out,indent=2));print(out)
