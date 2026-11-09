import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r165/source.blend'));s=bpy.context.scene
if not s.camera:bpy.ops.object.camera_add();s.camera=bpy.context.object
s.camera.location=(390,180,65);s.camera.rotation_euler=(Vector((240,370,48))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=145;s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.resolution_percentage=100;bpy.context.view_layer.update()
for p in [(224,309),(246,314),(237,354),(215,350)]:
 for z in [7,78]:
  q=world_to_camera_view(s,s.camera,Vector((*p,z)));print('POINT',p,z,q.x*1600,(1-q.y)*1400)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R254_OVAL_BUTUNLESIK_ADAY_v001.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('R165'):print('OBJECT',o.name,len(o.data.vertices))
