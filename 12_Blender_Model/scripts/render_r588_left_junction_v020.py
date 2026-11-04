import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for kind,path in [('source',R/'.local_source_cache/r316/museum_ring_reference.blend'),('model',R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v020.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 for o in s.objects:
  if o.name.startswith('R158_TREE_'):o.hide_render=True
 s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100
 bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
 views=[('top',(-19.5,9,40),(-19.5,9,-3.3),14),('oblique',(-20,3,2),(-19,9.5,-3.3),14)]if kind=='source'else[('glass',(-18,1,14),(-12,8,-3.3),15)]
 for label,position,target,width in views:
  s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=width;s.render.filepath=str(R/'renders/qa'/f'R588_left_join_v020_{kind}_{label}_final.png');bpy.ops.render.render(write_still=True)
