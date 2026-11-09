from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R175_DEMIRYOLU_VIYADUK_v001.blend'));out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith(('R16','R155','R156')):continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[k] for v in p) for k in range(3)];hi=[max(v[k] for v in p) for k in range(3)]
 if hi[1]>260 and hi[2]-lo[2]>3:out.append([o.name,lo,hi])
(R/'reports/R176_EXISTING_BUILDINGS.json').write_text(json.dumps(out,indent=2));print(out)
