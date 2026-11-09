import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R425_KULE_FOTOGRAF_TEPelikleri_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.name.startswith(('R154_','R172_','R195_','R198_','R199_','R303_','R319_','R321_')):continue
 q=[o.matrix_world@Vector(p) for p in o.bound_box];lo=[min(v[i] for v in q) for i in range(3)];hi=[max(v[i] for v in q) for i in range(3)]
 if hi[0]>-100 and lo[0]<-50 and hi[1]>-85 and lo[1]<-45:rows.append(dict(name=o.name,min=lo,max=hi))
(R/'reports/R426_FRONT_OBJECTS.json').write_text(json.dumps(rows,indent=2));print(rows)
