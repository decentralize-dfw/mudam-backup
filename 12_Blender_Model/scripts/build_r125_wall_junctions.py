from pathlib import Path
import bpy,bmesh,json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R124_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));out=B/'scenes/MUDAM_R125_ALT_KAT_VE_SERVIS_DUVAR_BIRLESIM_v002.blend';assert not out.exists();rows=[];changed=set()
def volume(o):
 bm=bmesh.new();bm.from_mesh(o.data);v=abs(bm.calc_volume());bm.free();return v
pairs=[('P11_WEST_STONE_BASE_17','P05_WEST_END'),('R19_STAGE_BACK_0','R19_FRONT_L_INNER'),('R19_STAGE_BACK_6','R19_FRONT_R_OUTER'),('R101_PASSAGE_SOUTH_SIDE','R96_DOCUMENTATION_EAST_WALL_8'),('R31_PASSAGE_SIDE_N','R31_EAST_JAMB_A'),('R31_PASSAGE_SIDE_S','R31_EAST_JAMB_B'),('R14_GALLERY_WALL_RETAINED','P05_GALLERY_HALL_WEST2')]
for name,other in pairs:
 o=bpy.data.objects[name];src=bpy.data.objects[other]
 if o.hide_render or src.hide_render:continue
 dep=bpy.context.evaluated_depsgraph_get()
 if o.modifiers:o.data=bpy.data.meshes.new_from_object(o.evaluated_get(dep),preserve_all_data_layers=True,depsgraph=dep);o.modifiers.clear()
 old=volume(o);original=o.data.copy();cut=src.copy();cut.data=bpy.data.meshes.new_from_object(src.evaluated_get(dep),preserve_all_data_layers=True,depsgraph=dep);cut.modifiers.clear();bpy.context.scene.collection.objects.link(cut);inv=cut.matrix_world.inverted();zs=[(cut.matrix_world@v.co).z for v in cut.data.vertices];mid=(min(zs)+max(zs))/2
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('R125 remove duplicate floor footprint','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True);new=volume(o)
 if old-new<1e-6:o.data=original;continue
 if new<1e-6:o.data=original;o.hide_render=True;o.hide_set(True)
 changed.add(name);o['R125_note']='Overlapping wall volume removed while retaining the original adjoining wall.';rows.append(dict(name=name,against=other,before_volume=old,after_volume=new,removed_overlap_volume=old-new))
for name in changed:
 o=bpy.data.objects[name]
 if o.hide_render:continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# Keep point-touching closed islands topologically separate after Boolean cuts.
for name in changed:
 o=bpy.data.objects[name]
 if o.hide_render:continue
 me=o.data;bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();bad=[e for e in bm.edges if len(e.link_faces)>2]
 if not bad:bm.free();continue
 groups=[];unseen=set(bm.faces)
 while unseen:
  seed=unseen.pop();group=[seed];stack=[seed]
  while stack:
   f=stack.pop()
   for e in f.edges:
    if len(e.link_faces)!=2:continue
    for g in e.link_faces:
     if g in unseen:unseen.remove(g);group.append(g);stack.append(g)
  groups.append(group)
 print('closed island split',name,[len(g) for g in groups]);assert len(groups)>1
 verts=[];faces=[];indices=[]
 for group in groups:
  if len(group)<4:
   print('discard isolated Boolean face',name,len(group));continue
  gb=bmesh.new();gv={}
  for face in group:
   for v in face.verts:
    if v not in gv:gv[v]=gb.verts.new(v.co)
   gb.faces.new([gv[v] for v in face.verts])
  gv_volume=abs(gb.calc_volume());gb.free();print('island volume',name,len(group),gv_volume)
  if gv_volume<1e-7:continue
  vm={}
  for f in group:
   ids=[]
   for v in f.verts:
    if v not in vm:vm[v]=len(verts);verts.append(tuple(v.co))
    ids.append(vm[v])
   faces.append(ids);indices.append(f.index)
 new=bpy.data.meshes.new(name+'_R125_ISLANDS');new.from_pydata(verts,[],faces);new.update()
 for mat in me.materials:new.materials.append(mat)
 for f,oldindex in zip(new.polygons,indices):f.material_index=me.polygons[oldindex].material_index
 for olduv in me.uv_layers:
  uv=new.uv_layers.new(name=olduv.name)
  for f,oldindex in zip(new.polygons,indices):
   for li,oi in zip(f.loop_indices,me.polygons[oldindex].loop_indices):uv.data[li].uv=olduv.data[oi].uv
 bm.free();o.data=new
for name in changed:
 o=bpy.data.objects[name]
 if o.hide_render:continue
 bm=bmesh.new();bm.from_mesh(o.data);isolated=[f for f in bm.faces if all(e.is_boundary for e in f.edges)]
 if isolated:
  print('remove disconnected Boolean sheet',name,len(isolated));bmesh.ops.delete(bm,geom=isolated,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
  if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
  bm.to_mesh(o.data)
 bm.free()
for name in changed:
 o=bpy.data.objects[name]
 if o.hide_render:continue
 bm=bmesh.new();bm.from_mesh(o.data)
 if all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)<0:
  bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data)
 bm.free()
assert changed
q=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(r['file']).name,closed_objects=[],changed_inherited_objects=sorted(changed),operations=rows,checked_pairs=pairs,source_ids=['102','103','104','R14','R19','R31','R96','R101'],construction_acceptance=False,visual_acceptance=False,limits=['Existing wall surfaces retained; duplicate intersection volumes removed. No new architectural dimensions.'])
bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R125_build_report.json').write_text(json.dumps(q,indent=2));print(rows)
