import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for label,path in [('candidate','scenes/MUDAM_R532_GUNEY_TAM_YAYA_ALANI_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(62,-48,65));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((62,-48,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=50;s.render.filepath=str(R/f'renders/qa/R532_south_road_wide_{label}.png');bpy.ops.render.render(write_still=True)







