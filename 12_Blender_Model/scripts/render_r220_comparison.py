import bpy
from pathlib import Path
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R220_ERASMUS_ARKA_BAGLANTI_ADAY_v001.blend'));s=bpy.context.scene;s.camera.location=(150,430,250);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=220;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R220_erasmus_source_comparison.png');bpy.ops.render.render(write_still=True)



