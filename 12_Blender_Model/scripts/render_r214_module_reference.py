from pathlib import Path
import bpy
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));s=bpy.context.scene;s.camera.location=(125,414,200);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.resolution_x=1300;s.render.resolution_y=1300;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R214_erasmus_module_reference.png');bpy.ops.render.render(write_still=True)
