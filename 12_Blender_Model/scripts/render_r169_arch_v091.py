from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_CATIPENCERE_v091.blend'));s=bpy.context.scene;s.cycles.samples=16
for name,delta in [('front',(22,-40,27)),('rear',(-20,31,30))]:
 target=Vector((-80,-301,-66));s.camera.location=target+Vector(delta);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/f'renders/qa/R169_architectural_{name}_v091.png');bpy.ops.render.render(write_still=True)
print('FINAL_LOCAL_VIEWS_SAVED')

