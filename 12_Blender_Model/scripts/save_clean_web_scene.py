from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R151_WEB_LOD_v002.blend'));removed=[]
for o in list(bpy.context.scene.objects):
 if o.type=='MESH' and o.name.startswith('R151_ACT_'):
  bounds=[o.matrix_world@Vector(c) for c in o.bound_box]
  if min((p.x*p.x+p.y*p.y)**.5 for p in bounds)<180:removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(R/'exports/r151_web_clean/near_context.glb'))
for o in bpy.context.selected_objects:
 if o.type=='MESH':o.name='R151_ACT_CLEAN_NEAR_'+o.name
bpy.ops.file.pack_all();bpy.ops.outliner.orphans_purge(do_recursive=True);target=R/'scenes/MUDAM_R151_WEB_CLEAN_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True);print('CLEAN_SAVED',len(removed),target.stat().st_size,flush=True)

