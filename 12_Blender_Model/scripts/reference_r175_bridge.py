from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'));s=bpy.context.scene;t=Vector((-220,-320,-60));s.camera.location=t+Vector((-100,-140,100));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=170;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R175_bridge_reference.png');bpy.ops.render.render(write_still=True)
