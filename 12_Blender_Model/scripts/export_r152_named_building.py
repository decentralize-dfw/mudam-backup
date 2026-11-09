"""Export the retained, registered museum with identity for the main web app."""
from pathlib import Path
import bpy, json
from mathutils import Vector
R = Path(__file__).resolve().parents[1]
out = R / '.local_source_cache/r152'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R151_WEB_CLEAN_v002.blend'))
objects = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.hide_render and o.visible_get() and not o.name.startswith('R151_ACT_')]
bpy.ops.object.select_all(action='DESELECT')
rows=[]
for o in objects:
    o.select_set(True)
    b=[o.matrix_world@Vector(c) for c in o.bound_box]
    rows.append(dict(name=o.name,level=o.get('level_id'),element=o.get('element_type'),bounds=[[min(p[k] for p in b) for k in range(3)],[max(p[k] for p in b) for k in range(3)]]))
(out/'building_objects.json').write_text(json.dumps(rows))
bpy.ops.export_scene.gltf(filepath=str(out/'building.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_yup=True)
print('R152_NAMED_BUILDING_EXPORTED',len(objects),flush=True)
