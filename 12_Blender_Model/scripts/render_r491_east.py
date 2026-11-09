import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for label,path in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('candidate','scenes/MUDAM_R490_TAM_KUZEYBATI_GECIT_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=700;s.render.resolution_y=700;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(60,-35,70));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((60,-35,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=32;s.render.filepath=str(R/f'renders/qa/R491_east_{label}.png');bpy.ops.render.render(write_still=True)
