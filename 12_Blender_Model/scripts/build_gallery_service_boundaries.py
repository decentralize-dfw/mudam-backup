"""Complete the long ground-gallery boundaries drawn in both official source plans."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base='MUDAM_R112_DOGU_GALERI_GECIT_ORTUSU_v001.blend'
out=B/'scenes/MUDAM_R113_GALERI_SERVIS_UZUN_DUVARLARI_v001.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
C=json.loads((B/'config/foundation.json').read_text())['calibration'];G=json.loads((B/'config/ground_gallery_access.json').read_text());P=json.loads((B/'config/ground_service_rooms.json').read_text())
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
made=[];records=[]
for side,xi,xo,ye in [('E',G['source_gallery_polygons']['E'][10][0],P['walls']['WC_E_W'][0][0],G['source_gallery_polygons']['E'][11][1]),('W',G['source_gallery_polygons']['W'][7][0],P['walls']['WC_W_E'][0][0],G['source_gallery_polygons']['W'][8][1])]:
 # Existing hall-side walls terminate at canonical y=555. The source gallery
 # boundary continues to its southern return, regardless of WC door openings.
 poly=[[xi,554.9],[xo,554.9],[xo,ye],[xi,ye]];top=P['ceiling_z'];vs=[pt(x,y,z) for z in [0,top] for x,y in poly]
 name=f'R113_{side}_GALLERY_SERVICE_BOUNDARY';me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.data.collections['90_UNCERTAIN_OR_PROXY'].objects.link(ob);me.materials.append(bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'])
 for k,v in dict(element_id=name,element_type='continuous_ground_gallery_service_boundary',level_id='L00',zone_id='GALLERY_'+side,source_ids='102,PDF2016',status='source_boundary_candidate_dimensions',assumption_note='Inner face follows archived gallery polygon; opposite side meets existing service-wall trace. Core width reconciles two existing source interpretations, not surveyed structural thickness. 4.35m head remains candidate. No gallery entrance or service doorway is filled.').items():ob[k]=v
 made.append(name);records.append(dict(name=name,side=side,inner_x=xi,outer_x=xo,y_range=[554.9,ye],z_range=[0,top],polygon=poly))
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=[],boundaries=records,construction_acceptance=False,limits=['Permanent uninterrupted gallery-service boundary drawn in102 and PDF2016; not temporary exhibition partitions.','WC and lobby doors on the service side remain unchanged.','Thickness is source-contour reconciliation; concealed construction and exact height remain unmeasured.'])
bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R113 long ground gallery service boundaries'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R113_build_report.json').write_text(json.dumps(r,indent=2),encoding='utf8');print('R113 two long wall bodies saved')
