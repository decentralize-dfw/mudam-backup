from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R123_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));rows=[];fail=[]
for pair in r['duplicate_pairs']:
 a=bpy.data.objects[pair['removed']];b=bpy.data.objects[pair['retained']];av=[a.matrix_world@v.co for v in a.data.vertices];bv=[b.matrix_world@v.co for v in b.data.vertices];distance=max([min((v-w).length for w in bv) for v in av]+[min((v-w).length for w in av) for v in bv]);ok=a.hide_render and not b.hide_render and b.visible_get() and distance<1e-5 and len(a.data.polygons)==len(b.data.polygons);rows.append(dict(removed=a.name,retained=b.name,max_vertex_distance_m=distance,retained_faces=len(b.data.polygons),ok=ok))
 if not ok:fail.append(a.name)
q=dict(file=r['file'],pairs=rows,failures=fail,construction_acceptance=False,scope='Coincident evaluated faces/materials checked before save, visibility and retained profile coverage checked after reopening.');(B/'reports/R123_verification.json').write_text(json.dumps(q,indent=2));print(rows)
