import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R327_DOGU_KALINTI_PLAN_ADAY_v001.blend'));rows=[]
for name in ['R152_RUIN_PARTITION_00','R152_RUIN_PARTITION_10','R152_PATH_824216705']:
 o=bpy.data.objects[name];rows.append(dict(name=name,vertices=[list(o.matrix_world@v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons]))
(R/'reports/R328_EXISTING_OUTER_WORKS.json').write_text(json.dumps(rows));print([(r['name'],len(r['vertices']),len(r['faces'])) for r in rows])
