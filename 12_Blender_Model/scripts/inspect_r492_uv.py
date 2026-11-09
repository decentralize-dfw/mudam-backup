import bpy,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R491_DOGU_ALT_HENDEK_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 m=re.match(r'R(\d+)_',o.name)
 if o.type!='MESH' or o.hide_render or not m or int(m.group(1))<316:continue
 missing=[];grass=False
 for mat in o.data.materials:
  if mat and mat.use_nodes:
   for n in mat.node_tree.nodes:
    if n.type=='UVMAP' and n.uv_map and n.uv_map not in o.data.uv_layers:missing.append((mat.name,n.uv_map))
   if mat.name=='R157_CONTINUOUS_LANDCOVER':grass=True
 if missing or grass:rows.append(dict(name=o.name,missing=missing,grass=grass,uv=[u.name for u in o.data.uv_layers]))
(R/'reports/R492_SITE_UV_AUDIT.json').write_text(json.dumps(rows,indent=2));print(rows)
