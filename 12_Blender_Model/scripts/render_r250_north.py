import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
for name,file in [('source','.local_source_cache/r171/north_reference.blend'),('authored','scenes/MUDAM_R249_ALT_MAHALLE_TEMEL_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/file));s=bpy.context.scene;c=s.camera;t=Vector((370,440,20));c.location=t+Vector((120,-190,140));c.rotation_euler=(t-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=170;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/f'renders/qa/R250_novotel_{name}.png');bpy.ops.render.render(write_still=True)
