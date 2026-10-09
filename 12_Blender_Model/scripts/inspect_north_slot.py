from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R79_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get() or not o.name.startswith('P11_GH_SLOT'):continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];lo=min(v.z for v in vs);hi=max(v.z for v in vs)
 if lo<4.3:rows.append(dict(name=o.name,z=[lo,hi],vertices=[list(v) for v in vs],kind=o.get('element_type','')))
(B/'reports/NORTH_SLOT_DIAGNOSIS.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print([(r['name'],r['z'],r['kind']) for r in rows])
