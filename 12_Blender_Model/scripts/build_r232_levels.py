from pathlib import Path
import bpy,bmesh,json,statistics
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R231_ERASMUS_CAM_BAGLANTI_ADAY_v001.blend'));d=json.loads((R/'config/r232_cross_bottom_projection.json').read_text());good=[r['z']for r in d['samples']if r['z']<9.9];base=statistics.median(good);changed=[]
for name in ['R231_GLAZED_SIDE_0','R231_GLAZED_SIDE_1','R231_GLAZED_END_0','R231_GLAZED_END_1']:
 o=bpy.data.objects[name];old=min(v.co.z for v in o.data.vertices)
 for v in o.data.vertices:
  if abs(v.co.z-old)<1e-4:v.co.z=base
 o.data.update();changed.append(dict(name=name,oldBase=old,newBase=base))
# Combine only intersecting roof solids; no source mesh is copied.
a=bpy.data.objects['R228_CURVED_GLAZED_ROOF'];b=bpy.data.objects['R231_CURVED_GLAZED_ROOF'];bpy.context.view_layer.objects.active=a;m=a.modifiers.new('T_ROOF_UNION','BOOLEAN');m.operation='UNION';m.solver='EXACT';m.object=b;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(b,do_unlink=True);a.name='R232_T_GLAZED_ROOF'
path=R/'scenes/MUDAM_R232_ERASMUS_ENINE_CAM_KOT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for o in bpy.context.scene.objects:o.select_set(o.name.startswith(('R228_','R231_','R232_')))
glb=R/'exports/r152_clean/r232_T_link_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(not c['boundary'] and not c['zero']for c in checks)
(R/'reports/R232_CROSS_LINK_LEVEL.json').write_text(json.dumps(dict(accepted=False,published=False,changes=changed,source=d,reopen=checks,limits=['Three visible projected underside observations only; fourth excluded above roof','Transverse member now shallow canopy; exact structural/glazing classification still unresolved','Longitudinal link side/base/end geometry and junction fascia overlaps remain provisional']),indent=2));print('R232_READY',base,checks)
