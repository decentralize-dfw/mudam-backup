import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R363_PAVYON_DOGU_ZEMIN_ADAY_v001.blend'));s=bpy.context.scene;bpy.ops.object.camera_add(location=(32,-50,90));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((32,-50,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75;s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_x=960;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R363_pavilion_candidate.png');bpy.ops.render.render(write_still=True)

