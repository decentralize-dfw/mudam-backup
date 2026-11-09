import bpy,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R577_KALE_DUVAR_KAPALI_KABUK_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 rev=re.match(r'R(\d+)_',o.name)
 if rev and int(rev[1])>=150:continue
 for m in o.data.materials:
  if not m or not m.use_nodes:continue
  for n in m.node_tree.nodes:
   if n.type=='UVMAP'and n.uv_map and n.outputs[0].is_linked and n.uv_map not in o.data.uv_layers:
    rows.append(dict(object=o.name,material=m.name,missingUv=n.uv_map,existing=list(o.data.uv_layers.keys())))
(R/'reports/R578_BUILDING_TEXTURE_UV_AUDIT.json').write_text(json.dumps(rows,indent=2));print('MISSING',len(rows));print(rows[:20])
