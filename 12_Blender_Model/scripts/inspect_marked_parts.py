from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'config/model_release.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['source_scene']));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 mats=[dict(name=m.name,color=list(m.diffuse_color)) for m in o.data.materials if m]
 if any('P05' in m['name'] or 'P06' in m['name'] for m in mats) or o.name.startswith(('R73_','R83_','R23_')):
  v=[o.matrix_world@v.co for v in o.data.vertices];rows.append(dict(name=o.name,mats=mats,vertices=[list(p) for p in v] if len(v)<40 else [],bounds=[[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)]))
(B/'reports/R94_diagnostic.json').write_text(json.dumps(rows,indent=2))
