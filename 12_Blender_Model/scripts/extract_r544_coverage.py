import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R540_KUZEY_KALINTI_SUR_HENDEK_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name.startswith(('R152_CLASS2','R322_','R525_','R321_','R523_'))):continue
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  if max(v.x for v in p)<-31 or min(v.x for v in p)>-26.8 or max(v.y for v in p)<1.5 or min(v.y for v in p)>4.4:continue
  rows.append([[v.x,v.y]for v in p])
(R/'reports/R544_EXISTING_COVERAGE.json').write_text(json.dumps(rows));print(len(rows))
