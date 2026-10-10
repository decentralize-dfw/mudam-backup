from pathlib import Path
import bpy,bmesh,json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R117_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));out=B/'scenes/MUDAM_R118_KOPRU_ESIK_CAKISMA_v001.blend';assert not out.exists();rows=[]
def volume(o):
 bm=bmesh.new();bm.from_mesh(o.data);v=abs(bm.calc_volume());bm.free();return v
for side in ['E','W']:
 o=bpy.data.objects[f'R117_{side}_BRIDGE_FLOOR_JOIN'];old=volume(o);threshold=bpy.data.objects[f'R23_THRESHOLD_{side}_BRIDGE'];cut=threshold.copy();cut.data=threshold.data.copy();bpy.context.scene.collection.objects.link(cut);inv=cut.matrix_world.inverted();zs=[(cut.matrix_world@v.co).z for v in cut.data.vertices];mid=(min(zs)+max(zs))/2
 for v in cut.data.vertices:
  p=cut.matrix_world@v.co;p.z=5.0 if p.z>mid else 4.4;v.co=inv@p
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('R118 retain original threshold footprint','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True);new=volume(o);assert 0<new<old-1e-5,(side,old,new);o['R118_note']='R117 floor connector trimmed around original R23 threshold footprint. Only previously missing side strips remain; existing threshold and its finish retained.';rows.append(dict(name=o.name,threshold=threshold.name,before_volume=old,after_volume=new,removed_overlap_volume=old-new))
q=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(r['file']).name,closed_objects=[],changed_inherited_objects=[x['name'] for x in rows],operations=rows,source_ids=['103','R23','R117'],construction_acceptance=False,visual_acceptance=False,limits=['No new architectural dimensions; removes duplicate floor volume from R117 connector around existing source103 threshold.'])
bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R118_build_report.json').write_text(json.dumps(q,indent=2));print(rows)
