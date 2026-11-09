import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];path=R/'scenes/MUDAM_R297_DOGU_GUNEY_CATI_MALZEME_ADAY_v001.blend';bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
s.camera.location=(250,77,180);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=150;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R297_south_roof_authored.png');bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.render.render(write_still=True)
