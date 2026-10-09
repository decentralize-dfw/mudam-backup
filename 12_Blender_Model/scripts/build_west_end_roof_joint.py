"""R91 reconcile the surviving P05 end wall with the revised P11 west roof."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base='MUDAM_R90_GUNEY_ATRIUM_CAM_CERCEVE_v001.blend';out=B/'scenes/MUDAM_R91_BATI_UC_DUVAR_CATI_v001.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));C=json.loads((B/'config/foundation.json').read_text())['calibration'];E=json.loads((B/'config/entry_package.json').read_text())['lower_roof']
def point(p,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*p[0]+ox;b=k*p[1]+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
o=bpy.data.objects['P05_WEST_END'];before=[o.matrix_world@v.co for v in o.data.vertices];assert len(before)==8
lo=point([862,161],E['low_eave_z']);hi=point([862,258],E['band_bottom_z']);cap=.20
assert (Vector((before[0].x,before[0].y,lo.z))-lo).length<.002
offset=before[5]-before[1];offset.z=0;after=[p.copy() for p in before]
# Keep the verified low-end miter and all ground elevations. Move the high end
# onto the registered revised roof endpoint, retaining the existing back offset.
for idx in [1,2]:after[idx].x=hi.x;after[idx].y=hi.y
for idx in [5,6]:after[idx].x=hi.x+offset.x;after[idx].y=hi.y+offset.y
for idx in [3,7]:after[idx].z=lo.z+cap
for idx in [2,6]:after[idx].z=hi.z+cap
o.data=o.data.copy();inv=o.matrix_world.inverted()
for v,p in zip(o.data.vertices,after):v.co=inv@p
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
o['source_ids']='097,093,102';o['wall_end_revision']='R91 old P05 top reconciled with revised P11 west roof; 200mm head clearance is unmeasured candidate'
o['assumption_note']='097 shows a narrow stone upstand beside the sloping glass. Old end wall retained obsolete P05 roof heights. Existing low miter and base retained; no structural wall design claimed.'
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=[o.name],changed_inherited_objects=[o.name],before_vertices=[list(p) for p in before],after_vertices=[list(p) for p in after],roof_endpoints=[list(lo),list(hi)],candidate_head_clearance_m=cap,source_ids=['097','093','102'],construction_acceptance=False,limits=['097 supports a sloping stone end adjoining glass rather than the obsolete tall P05 silhouette.','Current registered P11 roof endpoints and candidate heights reused; no new survey dimension introduced.','200mm upstand is an explicit visualization candidate, not measured coping or flashing.','Low miter and ground elevations retained; high endpoint reconciled to the revised roof line.'])
bpy.context.scene['stage']='R91 west end wall tied to revised glass roof';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R91_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R91_build_report.json').write_text(json.dumps(r,indent=2));print('R91 saved')
