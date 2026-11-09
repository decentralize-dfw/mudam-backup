import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for label,path in [('source',R/'.local_source_cache/r316/museum_ring_reference.blend'),('candidate',R/'scenes/MUDAM_R334_HENDEK_CAKISMA_TEMIZLIK_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;bpy.ops.object.camera_add(location=(32,-50,90));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((32,-50,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(R/f'renders/qa/R345_pavilion_{label}.png');bpy.ops.render.render(write_still=True)
