from pathlib import Path
import bpy,json
B=Path('12_Blender_Model');r=json.loads((B/'config/model_release.json').read_text());bpy.ops.wm.open_mainfile(filepath=r['source_scene']);rows=[]
for name in ['P05_WEST_END','P11_WEST_17_00_00','P11_WEST_17_00_05','P05_EAST_END']:
 o=bpy.data.objects.get(name)
 if o:rows.append(dict(name=name,vertices=[list(o.matrix_world@v.co) for v in o.data.vertices],hidden=o.hide_render))
(B/'reports/R90_end_geometry.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
