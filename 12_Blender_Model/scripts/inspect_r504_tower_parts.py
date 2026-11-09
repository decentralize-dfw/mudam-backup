import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R501_BATI_SUR_AGAC_KOTU_DUZELTME_ADAY_v001.blend'));out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not any(k in o.name for k in ['SOUTH','CENTRE','WEST']):continue
 v=[o.matrix_world@Vector(p) for p in o.bound_box];lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
 if lo[0]<-50 and hi[0]>-80 and lo[1]<-40 and hi[1]>-70:out.append(dict(name=o.name,min=lo,max=hi,materials=[m.name for m in o.data.materials if m],vertices=len(o.data.vertices)))
(R/'reports/R504_TOWER_PARTS.json').write_text(json.dumps(out,indent=2));print(out)
