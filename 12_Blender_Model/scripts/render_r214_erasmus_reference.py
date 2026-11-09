from pathlib import Path
import bpy
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));s=bpy.context.scene;s.camera.location=(150,430,250);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=220;s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R214_erasmus_source_top.png');bpy.ops.render.render(write_still=True)
