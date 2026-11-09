import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for label,path in [('source',R/'.local_source_cache/r316/museum_ring_reference.blend'),('candidate',R/'scenes/MUDAM_R365_PAVYON_SUR_TABAN_BIRLESIM_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;bpy.ops.object.camera_add(location=(90,-105,55));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((28,-36,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75;s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.filepath=str(R/f'renders/qa/R368_pavilion_oblique_{label}.png');bpy.ops.render.render(write_still=True)
