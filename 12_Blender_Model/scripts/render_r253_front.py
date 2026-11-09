import bpy
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));s=bpy.context.scene;t=Vector((320,398,18));s.camera.location=t+Vector((80,-100,0));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=80;s.render.resolution_x=1600;s.render.resolution_y=800;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R253_oval_front_source.png');bpy.ops.render.render(write_still=True)
