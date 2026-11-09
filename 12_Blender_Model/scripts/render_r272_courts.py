import bpy
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));s=bpy.context.scene;s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8
for label,p in [('left',(92.7,387.2,100)),('right',(165.9,450.55,100))]:
 s.camera.location=p;s.render.filepath=str(R/f'renders/qa/R272_{label}_court_source_top.png');bpy.ops.render.render(write_still=True)
