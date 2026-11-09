import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R400_KALE_CAM_BANT_AHSAP_TERAS_ADAY_v001.blend'));s=bpy.context.scene;bpy.ops.object.camera_add(location=(-28,-20,4.0));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-61.6,-53.15,2.8))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='PERSP';s.camera.data.lens=28;s.camera.data.clip_start=.05;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=667;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R400_rooftop_eye_candidate.png');bpy.ops.render.render(write_still=True)
