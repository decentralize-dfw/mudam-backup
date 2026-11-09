import bpy,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R525_BATI_TERAS_EGIMLI_KENAR_ADAY_v001.blend'))
records={}
for key in ['near']:
 names=[]
 for o in bpy.context.scene.objects:
  n=re.match(r'R(\d+)_',o.name);num=int(n[1])if n else 0
  choose=(o.name.startswith(('R152_','R154_'))or o.get('level_id')=='L00_APPROACH' or 317<=num<=525)if key=='near' else ((161<=num<=314 and num!=169) or o.name.startswith("ARCH_"))if key=='district'else o.name.startswith('R158_TREE_')
  selected=o.type=='MESH' and not o.hide_render and choose;o.select_set(selected)
  if selected:names.append(o.name)
 bpy.ops.export_scene.gltf(filepath=str(R/f'exports/r152_clean/r525_{key}_REVIEW.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
 records[key]=names;print('EXPORTED',key,len(names),flush=True)
(R/'reports/R525_EXPORT_SELECTION.json').write_text(json.dumps(records,indent=2))

import math
p=R/'exports/r152_clean/r525_near_REVIEW.glb';bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));errors=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  bad=sum(not all(math.isfinite(v) for v in p.co) for p in o.data.vertices);zero=sum(p.area<1e-10 for p in o.data.polygons)
  if bad or zero:errors.append(dict(name=o.name,nonFinite=bad,zeroArea=zero))
(R/'reports/R525_GLB_ROUNDTRIP.json').write_text(json.dumps(dict(bytes=p.stat().st_size,errors=errors,accepted=False,published=False),indent=2));print('ROUNDTRIP',errors)


