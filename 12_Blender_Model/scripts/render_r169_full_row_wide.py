from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r169/source.blend'));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.world=bpy.data.worlds.new('Black');s.world.color=(0,0,0);bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=56;s.camera.location=(-80,-301,30);s.camera.rotation_euler=(Vector((-80,-301,-65))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/qa/R169_full_row_source_wide.png');bpy.ops.render.render(write_still=True)


