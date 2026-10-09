"""R98 trim only the erroneous upper stair-wall extension into the source bridge."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];base=json.loads((B/'reports/R97_build_report.json').read_text());UP=base['upper_z'];out=B/'scenes/MUDAM_R98_UST_KOPRU_DUVAR_SINIRI_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B.parent/base['file']))
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
vs=[pt(x,y,z) for z in [UP,30] for x,y in [(450,555.5),(561,555.5),(561,597),(450,597)]];me=bpy.data.meshes.new('R98_TEMP');me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();cut=bpy.data.objects.new('R98_TEMP',me);bpy.context.scene.collection.objects.link(cut);changed=[]
def volume(me):
 bm=bmesh.new();bm.from_mesh(me);v=abs(bm.calc_volume(signed=True));bm.free();return v
for name in ['R45_STAIR_RECESS_CONTINUOUS','R04_RECESS_HEAD','R04_RECESS_TOP_LINTEL']:
 ob=bpy.data.objects[name];old=ob.data;v=volume(old);ob.data=old.copy();bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('R98 upper bridge clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
 if abs(volume(ob.data)-v)>1e-7:
  changed.append(name);ob['R98_note']='Upper extension beyond canonical y555.5 clipped above LP1 floor; source103 bridge remains a passage. Ground wall and stair treads preserved. Boundary follows visitor-plan topology, not survey precision.'
 else:ob.data=old
bpy.data.objects.remove(cut,do_unlink=True);assert changed
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(base['file']).name,closed_objects=changed,changed_inherited_objects=changed,upper_z=UP,source_boundary_y=555.5,construction_acceptance=False,limits=['103 upper plan bridge north edge y555..556; local topology correction, not survey dimensional acceptance.','Only identified stair-wall intrusion corrected. Other marked upper room/roof and lift areas remain under review.','All inherited stair treads, lower walls and floor retained.']);bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R98 upper bridge wall clearance';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R98_build_report.json').write_text(json.dumps(r,indent=2));print('R98 changed',changed)
