import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R548_BATI_HENDEK_EGIM_YENIDEN_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 bounds=[o.matrix_world@Vector(p)for p in o.bound_box]
 if max(v.x for v in bounds)<-25 or min(v.x for v in bounds)>5 or max(v.y for v in bounds)<-20 or min(v.y for v in bounds)>15:continue
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  if max(v.x for v in p)<-25 or min(v.x for v in p)>5 or max(v.y for v in p)<-20 or min(v.y for v in p)>15:continue
  rows.append([[v.x,v.y]for v in p])
(R/'reports/R549_COVERAGE.json').write_text(json.dumps(rows));print(len(rows))

