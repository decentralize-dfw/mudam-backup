"""R107 reconcile the original P17 floor trace with the retained R09 room walls."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];base=json.loads((B/'reports/R105_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/reading_room.json').read_text());Q=json.loads((B/'config/reading_void.json').read_text());out=B/'scenes/MUDAM_R107_OKUMA_DOSEME_DUVAR_TEMASI_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B.parent/base['file']));up=Vector((0,0,1))
def pt(p):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
poly=list(map(pt,P['room_inner_polygon']));center=sum(poly,Vector())/len(poly);target=[]
for i,p in enumerate(poly):
 a=(p-poly[i-1]).normalized();b=(poly[(i+1)%len(poly)]-p).normalized();n1=up.cross(a);n2=up.cross(b)
 if n1.dot(p-center)<0:n1=-n1
 if n2.dot(p-center)<0:n2=-n2
 bis=(n1+n2).normalized();target.append(p+bis*.005/bis.dot(n1))
ob=bpy.data.objects['P17_READING_FLOOR'];ob.data=ob.data.copy();before=[list(ob.matrix_world@v.co) for v in ob.data.vertices];records=[];iv=ob.matrix_world.inverted()
assert len(before)==16,'Unexpected revised floor topology; inspect before editing'
for i,old in enumerate(map(pt,Q['floor_outline_canonical'])):
 matches=[]
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co
  if Vector((p.x-old.x,p.y-old.y,0)).length<.0001:
   v.co=iv@Vector((target[i].x,target[i].y,p.z));matches.append(v.index)
 assert len(matches)==2,(i,matches)
 records.append(dict(corner=i,old_canonical=Q['floor_outline_canonical'][i],wall_canonical=P['room_inner_polygon'][i],target_world=list(target[i]),vertices=matches,delta_m=(old-target[i]).length))
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['R107_note']='Old visitor-trace outer floor perimeter reconciled to existing R09 source2016 room walls with5mm buried overlap. Central diamond void and three passage unions unchanged.'
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(base['file']).name,closed_objects=[ob.name],changed_inherited_objects=[ob.name],object=ob.name,before_world=before,records=records,overlap_m=.005,construction_acceptance=False,limits=['Existing R09 source2016 room contour retained; original P17 floor manual trace brought to that perimeter.','Central floor void, three source passage unions, wall positions, floor level, thickness and railing geometry remain unchanged.','015/016 verify the central void and continuous room enclosure family; they do not measure perimeter offsets or floor thickness.'])
assert max(x['delta_m'] for x in records)>.01
bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R107 reading floor perimeter meets source walls';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R107_build_report.json').write_text(json.dumps(r,indent=2));print('R107 8 floor corners; max reconciliation',max(x['delta_m'] for x in records))
