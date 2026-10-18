import bpy,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R314_ECCL_GUNEY_KOSE_OTURUM_ADAY_v001.blend'))
records={}
for key in ['near','district','vegetation']:
 names=[]
 for o in bpy.context.scene.objects:
  n=re.match(r'R(\d+)_',o.name);num=int(n[1])if n else 0
  choose=(o.name.startswith(('R152_','R154_'))or o.get('level_id')=='L00_APPROACH')if key=='near' else ((161<=num<=314 and num!=169) or o.name.startswith("ARCH_"))if key=='district'else o.name.startswith('R158_TREE_')
  selected=o.type=='MESH' and not o.hide_render and choose;o.select_set(selected)
  if selected:names.append(o.name)
 bpy.ops.export_scene.gltf(filepath=str(R/f'exports/r152_clean/r314_{key}_REVIEW.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
 records[key]=names;print('EXPORTED',key,len(names),flush=True)
(R/'reports/R314_EXPORT_SELECTION.json').write_text(json.dumps(records,indent=2))
