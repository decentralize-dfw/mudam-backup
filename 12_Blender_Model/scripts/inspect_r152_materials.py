import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R151_WEB_CLEAN_v002.blend'))
for o in bpy.context.scene.objects:
 if o.name.startswith('R35_WALL_51946353_'):
  print('WALL_MATS',o.name,[(m.name if m else '',[(n.type,getattr(n,'uv_map',''),getattr(getattr(n,'image',None),'name','')) for n in m.node_tree.nodes] if m and m.use_nodes else [])for m in o.data.materials],flush=True);break
print('VIEW',bpy.context.scene.view_settings.exposure,flush=True)
