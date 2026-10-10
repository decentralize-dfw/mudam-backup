from pathlib import Path
import bpy,bmesh,json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R121_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));out=B/'scenes/MUDAM_R122_UST_ORTU_YUZEY_BIRLESIM_v001.blend';assert not out.exists();rows=[];changed=set()
def volume(o):
 bm=bmesh.new();bm.from_mesh(o.data);v=abs(bm.calc_volume());bm.free();return v
pairs=[('R85_RETURN_CEILING_1','R85_RETURN_CEILING_0'),('R39_PUBLIC_CEILING_19','R28_W_FLAT_CEILING')]
for name,other in pairs:
 o=bpy.data.objects[name];src=bpy.data.objects[other]
 if o.hide_render or src.hide_render:continue
 dep=bpy.context.evaluated_depsgraph_get()
 if o.modifiers:o.data=bpy.data.meshes.new_from_object(o.evaluated_get(dep),preserve_all_data_layers=True,depsgraph=dep);o.modifiers.clear()
 old=volume(o);original=o.data.copy();cut=src.copy();cut.data=bpy.data.meshes.new_from_object(src.evaluated_get(dep),preserve_all_data_layers=True,depsgraph=dep);cut.modifiers.clear();bpy.context.scene.collection.objects.link(cut);inv=cut.matrix_world.inverted();zs=[(cut.matrix_world@v.co).z for v in cut.data.vertices];mid=(min(zs)+max(zs))/2
 for v in cut.data.vertices:
  p=cut.matrix_world@v.co;p.z=max(zs)+.1 if p.z>mid else min(zs)-.1;v.co=inv@p
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('R122 remove duplicate floor footprint','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True);new=volume(o)
 if old-new<1e-6:o.data=original;continue
 if new<1e-6:o.data=original;o.hide_render=True;o.hide_set(True)
 changed.add(name);o['R122_note']='Ceiling duplicate footprint removed; original cover extent and elevation retained.';rows.append(dict(name=name,against=other,before_volume=old,after_volume=new,removed_overlap_volume=old-new))
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
 new=bpy.data.meshes.new(name+'_R122_ISLANDS');new.from_pydata(verts,[],faces);new.update()
 for mat in me.materials:new.materials.append(mat)
 for f,oldindex in zip(new.polygons,indices):f.material_index=me.polygons[oldindex].material_index
 for olduv in me.uv_layers:
  uv=new.uv_layers.new(name=olduv.name)
  for f,oldindex in zip(new.polygons,indices):
   for li,oi in zip(f.loop_indices,me.polygons[oldindex].loop_indices):uv.data[li].uv=olduv.data[oi].uv
 bm.free();o.data=new
assert changed
q=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(r['file']).name,closed_objects=[],changed_inherited_objects=sorted(changed),operations=rows,checked_pairs=pairs,source_ids=['102','103','R28','R39','R85'],construction_acceptance=False,visual_acceptance=False,limits=['Existing ceiling boundaries retained; only duplicate volumes removed. No new measured dimensions.'])
bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R122_build_report.json').write_text(json.dumps(q,indent=2));print(rows)
