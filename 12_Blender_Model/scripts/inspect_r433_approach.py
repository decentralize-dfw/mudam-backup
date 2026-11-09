import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R431_KALE_KOPRUSU_AHSAP_KORKULUK_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not any(s in o.name for s in ['PATH','PAV','GROUND','TERRACE','ROAD']):continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if lo[0]<-60 and hi[0]>-95 and lo[1]<-40 and hi[1]>-92:rows.append(dict(name=o.name,min=lo,max=hi))
(R/'reports/R433_APPROACH_OVERLAP_OBJECTS.json').write_text(json.dumps(rows,indent=2));print(rows)
