"""Local review export: own architecture and inner source ground; outer context streams."""
from pathlib import Path
import bpy,json,gzip,hashlib,struct
R=Path(__file__).resolve().parents[1]
scene=R/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v011.blend'
out=R/'exports/MUDAM_R151_v011_candidate.glb';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(scene))
for o in bpy.context.scene.objects:
 if o.name.startswith('R151_ACT_'):o.hide_render=True;o.hide_set(True)
patches=json.loads((R/'reports/ACT2020_inner_ground_export.json').read_text())['tiles']
for row in patches:
 before=set(bpy.context.scene.objects)
 bpy.ops.import_scene.gltf(filepath=str(R/'.local_source_cache/act_context/inner_ground_glb'/row['file']))
 for o in set(bpy.context.scene.objects)-before:
  if o.type=='MESH':o.name='R151_INNER_GROUND_'+Path(row['file']).stem
bpy.ops.object.select_all(action='DESELECT');selected=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and not o.hide_render and o.visible_get():o.select_set(True);selected.append(o.name)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_yup=True)
raw=out.read_bytes();assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
gz=out.with_suffix('.glb.gz');gz.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0));assert gzip.decompress(gz.read_bytes())==raw
receipt=dict(revision='R151 v011 aday',url='../exports/'+gz.name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),gzip_bytes=gz.stat().st_size,scene=str(scene),meshes=len(selected),selected_names=selected,accepted=False,scope='Architecture plus inner source ground; outer ACT environment streams separately. Local review only.')
(R/'config/act_candidate_release.json').write_text(json.dumps(receipt,indent=2))
print('CANDIDATE_EXPORTED',len(raw),gz.stat().st_size,len(selected),flush=True)
