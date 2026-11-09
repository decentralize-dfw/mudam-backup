from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));s=bpy.context.scene;t=Vector((350,450,15));s.camera.location=t+Vector((50,-180,100));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=210;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.filepath=str(R/'renders/qa/R176_missing_east_source.png');bpy.ops.render.render(write_still=True)
