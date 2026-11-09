import bpy
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R221_ERASMUS_GERCEK_ACIKLIK_ADAY_v001.blend'));s=bpy.context.scene;c=s.camera;c.location=(171,366,27);c.rotation_euler=(Vector((126,414,6))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=65;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R221_erasmus_front_authored.png');bpy.ops.render.render(write_still=True)

