import bpy
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
for f in ['.local_source_cache/r171/north_reference.blend','scenes/MUDAM_R247_ERASMUS_AVLU_SALON_ADAY_v001.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f));s=bpy.context.scene;c=s.camera;print('CAM',f,c.data.shift_x,c.data.shift_y,c.scale[:],c.parent,s.render.pixel_aspect_x,s.render.pixel_aspect_y,flush=True)
