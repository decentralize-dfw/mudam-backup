import bpy,bmesh,json
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R261_KULE_SERVIS_BOSLUKLARI_ADAY_v001.blend'))
o=bpy.data.objects['R257_CONTINUOUS_PITCHED_ROOF_0'];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R261_KULE_SERVIS_BOSLUKLARI_ADAY_v002.blend'),compress=True)
for o in bpy.context.scene.objects:o.select_set(o.name.startswith(('R255_','R256_','R257_','R258_','R261_')))
glb=R/'exports/r152_clean/r261_towers_REVIEW_v002.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R261_V002_REOPEN.json').write_text(json.dumps(dict(accepted=False,published=False,checks=checks),indent=2));print('R261_V002',len(checks),sum(c['boundary'] for c in checks),sum(c['zero'] for c in checks),flush=True)
