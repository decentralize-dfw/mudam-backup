import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R258_KULE_KAYNAK_SILUET_ADAY_v001.blend'));holes=[[(415,452),(453,420),(670,674),(632,706)],[(640,736),(680,702),(855,959),(815,993)]];ops=0
for i,pixels in enumerate(holes):
 ring=[(211+x*.05,443-y*.05) for x,y in pixels];v=[(x,y,z) for z in [88.5,105] for x,y in ring];f=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];me=bpy.data.meshes.new('CUT');me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();cut=bpy.data.objects.new('CUT',me);bpy.context.collection.objects.link(cut)
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH' or not o.name.startswith(('R257_CONTINUOUS_PITCHED_ROOF',)):continue
  xs=[p[0] for p in ring];ys=[p[1] for p in ring];pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  if max(p.x for p in pts)<min(xs) or min(p.x for p in pts)>max(xs) or max(p.y for p in pts)<min(ys) or min(p.y for p in pts)>max(ys):continue
  bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Source service recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);ops+=1;print('CUT_DONE',i,o.name,flush=True)
  if not o.data.polygons:bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.objects.remove(cut,do_unlink=True)
print('ROOFS_CUT',flush=True)
path=R/'scenes/MUDAM_R259_KULE_SERVIS_GIRINTILERI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.camera.location=(246,408,220);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=70;s.render.resolution_x=1400;s.render.resolution_y=1400;s.cycles.samples=16;s.render.filepath=str(R/'renders/qa/R259_roof_top_authored.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R255_','R256_','R257_','R258_')))
glb=R/'exports/r152_clean/r259_towers_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R259_ROOF_RECESSES.json').write_text(json.dumps(dict(accepted=False,published=False,sourcePolygonsPixels=holes,booleanOperations=ops,checks=checks,limits=['Service pit side linings and equipment unresolved','Compare roof outline and all facades before acceptance']),indent=2));print('R259_CHECKS',len(checks),sum(c['boundary'] for c in checks),sum(c['zero'] for c in checks),flush=True)

