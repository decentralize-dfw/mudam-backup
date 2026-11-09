import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
for label,scene in [('current',R/'scenes/MUDAM_R585_DOGU_HENDEK_CIFT_ZEMIN_TEMIZ_ADAY_v001.blend'),('source',R/'.local_source_cache/r316/museum_ring_reference.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(scene))
 s=bpy.context.scene
 if label=='current':
  for o in s.objects:
   if o.name.startswith('R158_TREE_'):o.hide_render=True
 s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100
 bpy.ops.object.camera_add(location=(-62,-19,39));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-35,5,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=56
 s.render.filepath=str(R/f'renders/qa/R586_west_{label}.png');bpy.ops.render.render(write_still=True)
