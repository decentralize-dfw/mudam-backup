"""Restore the missing cover over the west ground gallery approach, not its removed wall."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
B=Path(__file__).resolve().parents[1];R=B.parent
base='MUDAM_R109_SERVIS_MERDIVEN_ALTI_KOSELERI_v001.blend'
out=B/'scenes/MUDAM_R111_KAFE_GECIT_UST_ORTUSU_v002.blend'
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
C=json.loads((B/'config/foundation.json').read_text())['calibration']
P=json.loads((B/'config/ground_gallery_access.json').read_text())
def pt(p,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*p[0]+ox;b=k*p[1]+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
# North band ends at v=578, before the separate west stair flight.
# Its rear meets the R96 retained upper-floor edge u=1160.61.
# Inner end overlaps the established ground-gallery ceiling boundary.
poly=[[687.8,431.8],[849,271],[869.305,291.305],[806.305,354.305],[798,385.2],[785,385.2],[717,452],[717,469],[687.8,469]]
z=P['ceiling_z'];top=z+P['ceiling_thickness'];ps=[pt(p,z) for p in poly];n=len(ps)
lookup={tuple(v):i for i,v in enumerate(ps)}
def ix(v):return v if isinstance(v,int) else lookup[tuple(v)]
tri=tessellate_polygon([ps]);faces=[tuple(ix(v) for v in reversed(t)) for t in tri]+[tuple(ix(v)+n for v in t) for t in tri]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
name='R111_W_GALLERY_APPROACH_SOFFIT';me=bpy.data.meshes.new(name);me.from_pydata(ps+[p+Vector((0,0,top-z)) for p in ps],[],faces);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
o=bpy.data.objects.new(name,me);bpy.data.collections['90_UNCERTAIN_OR_PROXY'].objects.link(o);me.materials.append(bpy.data.materials['P05_NEUTRAL_ENVELOPE'])
for k,v in dict(element_id=name,element_type='ground_passage_cover_candidate',zone_id='WEST_CAFE_GALLERY_APPROACH',level_id='L00',source_ids='102,PDF2016,093,user_SS4',status='conditional_cover_pending_visual_acceptance',assumption_note='Cover across existing approach footprint, joins candidate 4.35m gallery ceiling. Ground route remains open. Exact soffit elevation and concealed structure unmeasured; not a new upper accessible floor.').items():o[k]=v
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=[name],changed_inherited_objects=[],polygon_canonical=poly,z_range=[z,top],construction_acceptance=False,limits=['No reinstatement of the ground cafe diagonal wall removed by user.','Soffit datum inherits ground gallery ceiling; exact build-up and elevation remain conditional.','Spiral stair and eastern high portal not covered; separate source-based correction remains open.','This candidate must pass visual and circulation checks before becoming current.'])
bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R111 west gallery approach cover candidate'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R111_build_report.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print('R111 candidate saved')
