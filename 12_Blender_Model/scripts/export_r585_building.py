import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R149_UST_DOLASIM_TAS_DOSEME_v001.blend'))
names={o.name for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and o.visible_get() and o.get('level_id')!='L00_APPROACH'}
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R585_DOGU_HENDEK_CIFT_ZEMIN_TEMIZ_ADAY_v001.blend'))
found=[]
for o in bpy.context.scene.objects:
 o.select_set(o.name in names and not o.hide_render)
 if o.select_get():found.append(o.name)
missing=names-set(found)
allowed=('R35_WALL_','R35_MOAT_','R38_','R56_TREE_','R130_TREE_','R132_MAPPED_','R68_WALL_','R68_MOAT_')
assert all(n.startswith(allowed) or (n in bpy.data.objects and bpy.data.objects[n].hide_render) for n in missing),sorted(n for n in missing if not n.startswith(allowed))
(R/'reports/R585_INHERITED_CONTEXT_HIDDEN.json').write_text(json.dumps(sorted(missing),indent=2))
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r585_building_REVIEW.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
(R/'reports/R585_BUILDING_EXPORT_SELECTION.json').write_text(json.dumps(found,indent=2));print('EXPORTED',len(found),flush=True)

