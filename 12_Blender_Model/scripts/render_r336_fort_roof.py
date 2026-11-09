import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));s=bpy.context.scene;bpy.ops.object.camera_add(location=(-42,-34,100));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-42,-34,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R336_fort_roof_source.png');bpy.ops.render.render(write_still=True)
