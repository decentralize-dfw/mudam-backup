import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R487_KUZEYBATI_ALT_GECIT_ADAY_v001.blend'));out={}
for name in ['R485_NW_HISTORIC_RETAINING_WALL','R152_HISTORIC_WALL_49911001','R35_WALL_51946353_04_0','R457_NORTH_LOADING_COURT','R152_CLASS2_TERRAIN']:
 o=bpy.data.objects.get(name)
 if o:out[name]=[dict(name=m.name,nodes=[(n.type,n.image.filepath if n.type=='TEX_IMAGE' and n.image else '') for n in m.node_tree.nodes]) for m in o.data.materials if m]
(R/'reports/R487_MATERIAL_INSPECT.json').write_text(json.dumps(out,indent=2));print(out)
