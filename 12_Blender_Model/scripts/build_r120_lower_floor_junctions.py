from pathlib import Path
import bpy,bmesh,json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R119_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));out=B/'scenes/MUDAM_R120_ALT_KAT_DOSEME_BIRLESIM_v001.blend';assert not out.exists();rows=[];changed=set()
def volume(o):
 bm=bmesh.new();bm.from_mesh(o.data);v=abs(bm.calc_volume());bm.free();return v
pairs=[('R19_ENTRY_FLOOR_L','R29_FOYER_FLOOR'),('R19_ENTRY_FLOOR_R','R29_FOYER_FLOOR'),('R19_ROOM_FLOOR','R29_FOYER_FLOOR'),('R29_E_FLOOR','R29_FOYER_FLOOR'),('R29_W_FLOOR','R29_FOYER_FLOOR')]
for name,other in pairs:
 o=bpy.data.objects[name];src=bpy.data.objects[other]
 if o.hide_render or src.hide_render:continue
 old=volume(o);original=o.data.copy();cut=src.copy();cut.data=src.data.copy();bpy.context.scene.collection.objects.link(cut);inv=cut.matrix_world.inverted();zs=[(cut.matrix_world@v.co).z for v in cut.data.vertices];mid=(min(zs)+max(zs))/2
 for v in cut.data.vertices:
  p=cut.matrix_world@v.co;p.z=-5.2 if p.z>mid else -5.8;v.co=inv@p
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('R120 remove duplicate floor footprint','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True);new=volume(o)
 if old-new<1e-6:o.data=original;continue
 if new<1e-6:o.data=original;o.hide_render=True;o.hide_set(True)
 changed.add(name);o['R120_note']='Threshold/return floor trimmed to adjoining original finished-floor edge; duplicate top face removed, opening and finished level unchanged.';rows.append(dict(name=name,against=other,before_volume=old,after_volume=new,removed_overlap_volume=old-new))
for name in changed:
 o=bpy.data.objects[name]
 if o.hide_render:continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
assert changed
q=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(r['file']).name,closed_objects=[],changed_inherited_objects=sorted(changed),operations=rows,checked_pairs=pairs,source_ids=['104','R19','R29'],construction_acceptance=False,visual_acceptance=False,limits=['Existing registered gallery floors and thresholds retained; only duplicate coverage removed. No new measured dimensions.'])
bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R120_build_report.json').write_text(json.dumps(q,indent=2));print(rows)
