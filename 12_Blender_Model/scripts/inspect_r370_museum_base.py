import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R365_PAVYON_SUR_TABAN_BIRLESIM_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 pts=[o.matrix_world@v.co for v in o.data.vertices];mi=[min(v[i] for v in pts) for i in range(3)];ma=[max(v[i] for v in pts) for i in range(3)]
 if ma[0]<10 or mi[0]>55 or ma[1]<-33 or mi[1]>-15 or mi[2]>1 or ma[2]<-6:continue
 if len(pts)>30000:continue
 if not any(w in o.name.upper() for w in ['WALL','DUVAR','BASE','FACADE','CEPHE','R35','R29','R96']):continue
 rows.append(dict(name=o.name,bounds=[mi,ma]))
(R/'reports/R370_MUSEUM_BASE_OBJECTS.json').write_text(json.dumps(rows,indent=2));print(rows)
