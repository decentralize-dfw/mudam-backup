import bpy,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R577_KALE_DUVAR_KAPALI_KABUK_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH'or o.hide_render:continue
 r=re.match(r'R(\d+)_',o.name)
 if not r or int(r[1])>=150:continue
 area=sum(p.area for p in o.data.polygons)
 if area<15:continue
 mats=[m.name for m in o.data.materials if m];rows.append(dict(name=o.name,area=area,faces=len(o.data.polygons),materials=mats,level=o.get('level_id')))
(R/'reports/R579_BUILDING_BAKE_SURFACES.json').write_text(json.dumps(rows,indent=2));print('SURFACES',len(rows));print(rows[:35])
