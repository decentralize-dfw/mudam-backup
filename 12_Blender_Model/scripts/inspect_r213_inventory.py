import bpy,json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R213_PALAIS_GIRIS_ZEMINLERI_v002.blend'))
a=[dict(name=o.name,mesh=o.data.name,polys=len(o.data.polygons),hidden=o.hide_render)for o in bpy.context.scene.objects if o.type=='MESH'];(R/'reports/R213_INVENTORY.json').write_text(json.dumps(a));print(collections.Counter(x['name'].split('_')[0]for x in a));print([x for x in a if x['name'].startswith(('R154','R169','ARCH_'))][:35])
