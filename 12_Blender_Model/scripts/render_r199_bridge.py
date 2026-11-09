from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'))
s=bpy.context.scene;t=Vector((-193,-170,-17));s.camera.location=t+Vector((32,-40,30));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=48;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.filepath=str(R/'renders/qa/R199_bridge_reference.png');bpy.ops.render.render(write_still=True)
