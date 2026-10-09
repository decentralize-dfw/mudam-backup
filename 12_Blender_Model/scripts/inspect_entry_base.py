from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_R83_CATI_KENAR_KAPANISLARI_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and not o.hide_render and o.visible_get() and (o.name.startswith('ENT-') or o.name.startswith('P12_')):
  vs=[o.matrix_world@v.co for v in o.data.vertices];lo=min(p.z for p in vs);hi=max(p.z for p in vs)
  if lo<.5:rows.append(dict(name=o.name,bottom=lo,top=hi))
(B/'reports/ENTRY_BASE_DIAGNOSTIC.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
