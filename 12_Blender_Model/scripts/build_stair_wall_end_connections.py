"""R76: reconcile two disconnected stair/gallery wall ends against existing source boundaries."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R75_ODITORYUM_DUVAR_BIRLESIMLERI_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R76_MERDIVEN_DUVAR_UCLARI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));C=json.loads((B/'config/foundation.json').read_text())['calibration'];changed=[];records=[]
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def update(ob,world,note):
 old=[list(ob.matrix_world@v.co) for v in ob.data.vertices];ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
 for v,w in zip(ob.data.vertices,world):v.co=inv@w
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob['wall_end_revision']='R76 '+note;changed.append(ob.name);records.append(dict(name=ob.name,before_world_vertices=old,after_world_vertices=[list(w) for w in world],note=note))
# Upper east diagonal is a truncated continuation of the PDF gallery boundary.
ob=bpy.data.objects['R10_UPPER_DIAGONAL_WALL'];world=[ob.matrix_world@v.co for v in ob.data.vertices];target=json.loads((B/'config/upper_gallery_room.json').read_text())['source_polygons_canonical']['E'][2];delta=point(*target)-Vector((world[1].x,world[1].y,0))
for i in [1,2,5,6]:world[i]+=delta
update(ob,world,'East end extended to existing PDF gallery corner; start and height fixed.')
# Lower west stub had the opposite thickness side and did not reach R07.
# Align its room face with x688, retain its source end, width and z extents.
ob=bpy.data.objects['R29_W_DIVIDER_END'];world=[ob.matrix_world@v.co for v in ob.data.vertices];low=min(v.z for v in world);high=max(v.z for v in world);scale,dx,dy=C['basement_registration']['source_to_canonical'];yend=393*scale+dy;th=.25/C['meters_per_canonical_pixel'];poly=[(688,429.99),(688,yend),(688+th,yend),(688+th,429.99)];world=[point(x,y,z) for z in [low,high] for x,y in poly];update(ob,world,'West stub aligned to existing R07 inner face; original y393 access termination, 250mm width and heights retained. 0.01 canonical pixel overlap is numerical join tolerance.')
report=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=changed,changed_inherited_objects=changed,records=records,east_endpoint_translation_m=delta.length,west_original_plan_face_x=623*scale+dx,west_new_plan_face_x=688,west_face_shift_m=(688-(623*scale+dx))*C['meters_per_canonical_pixel'],construction_acceptance=False,limits=['Small source-registration discrepancies are reconciled to the already established adjoining wall; not new measured dimensions.','East diagonal end reaches existing source corner; its start and z extents remain fixed.','West stub width remains a candidate; thickness side corrected to match the adjoining stone wall.','Full staircase and roof/glass coordination remain later system checks.'])
bpy.context.scene['stage']='R76 stair wall end continuity';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R76_SOURCE_AND_LIMITS').write(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R76_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R76 east end extension',delta.length,'west face shift',report['west_face_shift_m'])
