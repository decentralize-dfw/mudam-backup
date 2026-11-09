from pathlib import Path
import bpy
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
for tag,path in [('source',R/'.local_source_cache/r171/fort_reference.blend'),('model',R/'scenes/MUDAM_R236_KALE_AVLU_YOL_OTURUM_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;t=Vector((-229.6,-192.1,-18));s.camera.location=t+Vector((35,-45,45));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/f'renders/qa/R239_ruin_{tag}.png');bpy.ops.render.render(write_still=True)
