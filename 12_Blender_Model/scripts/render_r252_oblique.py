import bpy
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));s=bpy.context.scene;t=Vector((320,398,20));s.camera.location=t+Vector((80,-100,80));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R252_oval_source_oblique.png');bpy.ops.render.render(write_still=True)
