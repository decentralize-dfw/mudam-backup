"""Complete ground-gallery opaque wall bodies between saved inner and outer bounds."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R77_BATI_UC_DUVAR_BAGLANTISI_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R78_ZEMIN_GALERI_DUVAR_GOVDELERI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/ground_gallery_access.json').read_text());M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def point(p,z=0):
 x,y=p;a=k*x+off[0];b=k*y+off[1];return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def canonical(p):
 a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2];u=(M[1][1]*a-M[0][1]*b)/det;v=(-M[1][0]*a+M[0][0]*b)/det;return [(u-off[0])/k,(v-off[1])/k]
def verts(name):return [canonical(bpy.data.objects[name].matrix_world@v.co) for v in bpy.data.objects[name].data.vertices]
E=P['source_gallery_polygons']['E'];W=P['source_gallery_polygons']['W'];frontE=verts('P05_FRONT_0');frontW=verts('P05_FRONT_10');diagonal=verts('P05_FRONT_9');xe=frontE[4][0];xw=frontW[4][0];a,b=diagonal[4],diagonal[5]
def diagx(y):return a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
def diagy(x):return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
# PDF gallery paths 115/116 supply the inner finish boundary. Existing facade
# back faces supply the other side; this is not a measured structural wall width.
polys={'E':[[xe,E[1][1]],[E[1][0],E[1][1]],[E[0][0],E[0][1]],[xe,E[0][1]]],
'W':[W[1],W[0],W[-1],W[-2],W[-3],W[-4],[diagx(W[-4][1]),W[-4][1]],[xw,diagy(xw)],[xw,W[1][1]]]}
root=bpy.data.collections.new('R78_GROUND_GALLERY_WALL_BODIES');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];records=[]
for side,poly in polys.items():
 n=len(poly);vs=[point(p,z) for z in [0,P['ceiling_z']] for p in poly];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];name=f'R78_{side}_GROUND_GALLERY_WALL_BODY';me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'])
 for key,value in dict(element_id=name,element_type='ground_gallery_wall_envelope_candidate',zone_id='GALLERY_'+side,level_id='L00',source_ids='102,PDF2016,056,061,062',status='conditional_dual_boundary_envelope',confidence_xy='C saved PDF room and outer facade boundaries',confidence_z='D inherited 4.35m ceiling',assumption_note='Core between existing inner/outer source boundaries; not surveyed thickness or inferred structural layers. Upper floor and roof unchanged.').items():ob[key]=value
 made.append(name);records.append(dict(name=name,canonical_polygon=poly,z_range=[0,P['ceiling_z']]))
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=[],wall_bodies=records,source_config='ground_gallery_access.json',source_vector_paths={'W_gallery':116,'wall_ink':0},construction_acceptance=False,limits=['Existing PDF gallery inner boundaries and facade backs retained; wide core is source reconciliation, not measured wall build-up.','Only L00 opaque side boundaries; front east windows, all source entry portals, upper circulation and roof untouched.','No artwork or exhibition partitions added. Fixed gallery boundary supported by 2016 wall ink and visitor scheme.'])
bpy.context.scene['stage']='R78 ground gallery wall body continuity';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R78_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R78_build_report.json').write_text(json.dumps(r,indent=2),encoding='utf8');print('R78',len(made),'wall bodies')
