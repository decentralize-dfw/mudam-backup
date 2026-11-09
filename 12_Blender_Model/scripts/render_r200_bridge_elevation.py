from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/bridge_reference.blend'));d=json.loads((R/'reports/R175_BRIDGE_MEASUREMENTS.json').read_text());a=Vector((*d['a'],0));u=Vector((*d['u'],0));n=Vector((*d['n'],0));t=a+u*100+Vector((0,0,-57));s=bpy.context.scene;s.camera.location=t+n*150;s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=240;s.render.resolution_x=1600;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R200_bridge_full_source_elevation.png');bpy.ops.render.render(write_still=True)

