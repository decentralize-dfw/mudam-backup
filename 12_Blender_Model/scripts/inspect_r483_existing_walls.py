import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R464_AVLU_CAMI_ZEMIN_KESISI_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not any(k in o.name.upper() for k in ['WALL','MASON','FORT','SUR','RUIN']):continue
 b=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in b) for i in range(3)];hi=[max(v[i] for v in b) for i in range(3)]
 if hi[0]<-60 or lo[0]>-25 or hi[1]<20 or lo[1]>50:continue
 rows.append(dict(name=o.name,hidden=o.hide_render,lo=lo,hi=hi))
(R/'reports/R483_NW_EXISTING_WALLS.json').write_text(json.dumps(rows,indent=2));print(rows)
