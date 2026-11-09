import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R525_BATI_TERAS_EGIMLI_KENAR_ADAY_v001.blend'));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-10,-15,220));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-10,-15,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=220;s.render.filepath=str(R/'renders/qa/R525_museum_ring_candidate.png');bpy.ops.render.render(write_still=True)

