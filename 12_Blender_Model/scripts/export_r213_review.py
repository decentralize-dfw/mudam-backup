import bpy,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R213_PALAIS_GIRIS_ZEMINLERI_v002.blend'))
records={}
for key in ['near','district','vegetation']:
 names=[]
 for o in bpy.context.scene.objects:
  n=re.match(r'R(\d+)_',o.name);num=int(n[1])if n else 0
  choose=(o.name.startswith(('R152_','R154_'))or o.get('level_id')=='L00_APPROACH')if key=='near' else (161<=num<=213 and num!=169)if key=='district'else o.name.startswith('R158_TREE_')
  selected=o.type=='MESH' and not o.hide_render and choose;o.select_set(selected)
  if selected:names.append(o.name)
 bpy.ops.export_scene.gltf(filepath=str(R/f'exports/r152_clean/r213_{key}_REVIEW.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
 records[key]=names;print('EXPORTED',key,len(names),flush=True)
(R/'reports/R213_EXPORT_SELECTION.json').write_text(json.dumps(records,indent=2))
