import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R334_HENDEK_CAKISMA_TEMIZLIK_ADAY_v001.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not ('HISTORIC_WALL' in o.name or 'RUIN_PARTITION' in o.name):continue
 pts=[o.matrix_world@v.co for v in o.data.vertices];mins=[min(v[i] for v in pts) for i in range(3)];maxs=[max(v[i] for v in pts) for i in range(3)]
 if mins[0]>55 or maxs[0]<-7 or mins[1]>-20 or maxs[1]<-60:continue
 rows.append(dict(name=o.name,min=mins,max=maxs,vertices=[list(v) for v in pts] if True else []))
(R/'reports/R353_PAVILION_WALLS.json').write_text(json.dumps(rows,indent=2));print([(r['name'],r['min'],r['max']) for r in rows])

