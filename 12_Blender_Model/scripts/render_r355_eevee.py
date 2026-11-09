import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R355_PAVYON_SUR_DONUSU_ADAY_v001.blend'));s=bpy.context.scene;bpy.ops.object.camera_add(location=(32,-50,90));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((32,-50,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75;s.render.engine='BLENDER_EEVEE_NEXT';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_x=960;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R355_pavilion_eevee.png');bpy.ops.render.render(write_still=True)

