from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R152_TEMIZ_YAKIN_CEVRE_v008.blend'))
s=bpy.context.scene
removed=[]
for o in list(s.objects):
 if o.name.startswith('R152_TREE_'):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
col=bpy.data.collections['R152_CLEAN_NEAR_SITE']
cam=s.camera;cam.location=(160,-215,170);cam.rotation_euler=(Vector((0,-5,-2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45
s.render.filepath=str(R/'renders/qa/R152_clean_no_placeholder_trees.png');bpy.ops.render.render(write_still=True)
out=R/'scenes/MUDAM_R152_TEMIZ_YAKIN_CEVRE_v009.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
exp=R/'exports/r152_clean';exp.mkdir(exist_ok=True);bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:
 if o.type=='MESH':o.select_set(True)
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and o.get('level_id')=='L00_APPROACH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(exp/'near_site.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and o.visible_get() and o.name not in col.objects and o.get('level_id')!='L00_APPROACH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(exp/'building.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)

p=R/'reports/R152_CLEAN_SITE_BUILD.json';report=json.loads(p.read_text());report.update(scene=str(out),trees=0,new_objects=len(col.objects),removed_placeholder_tree_objects=len(removed));p.write_text(json.dumps(report,indent=2));print('R152_V009_TREE_REMOVAL_COMPLETE',len(removed),flush=True)
