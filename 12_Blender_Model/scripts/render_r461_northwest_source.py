import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-48,37,90));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=35;s.render.filepath=str(R/'renders/qa/R461_northwest_grade_source.png');bpy.ops.render.render(write_still=True)
