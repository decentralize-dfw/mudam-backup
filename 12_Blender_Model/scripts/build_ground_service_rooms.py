"""R33 source-supported detached entrance walls and gallery finish candidates."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/ground_service_rooms.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R33_ZEMIN_SERVIS_MEKAN_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P16_GROUND_SERVICE_ENVELOPES');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];up=Vector((0,0,1));white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'];wood=bpy.data.materials['R23_GALLERY_WOOD_FLOOR_CANDIDATE'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE']
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);vs=[tuple(p+up*z) for z in [z0,z1] for p in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='L00',zone_id='GROUND_SERVICES',source_ids=','.join(P['source_ids']),confidence_xy='C diagram topology; thickness conditional',confidence_z='D candidate',confidence_detail='D unmeasured',status='conditional_plan_service_envelope',assumption_note='Source wall centreline interpretation; thickness, head and finishes unmeasured.').items():o[k]=v
 made.append(name);return o
TOP=P['ceiling_z'];th=P['wall_thickness_m']
for name,ends in P['walls'].items():
 a,b=[point(*p) for p in ends];n=(b-a).normalized().cross(up)*th/2;prism('R33_WALL_'+name,[a-n,b-n,b+n,a+n],0,TOP,white,'plan_service_wall_candidate')
for name,poly in P['ceiling_polygons'].items():prism('R33_CEILING_'+name,[point(*p) for p in poly],TOP,TOP+P['ceiling_thickness_m'],white,'service_ceiling_candidate')
for name,poly in P['missing_floor_polygons'].items():prism('R33_FLOOR_'+name,[point(*p) for p in poly],-.2,0,stone,'service_floor_connection_candidate')
# 102 and PDF120 show an open central ground-level passage; P05 proxy closes it.
old=bpy.data.objects['P05_MAIN_ATRIUM_BASE_4'];old.hide_render=True;old.hide_set(True);changed.append(old.name)
ob=old.copy();ob.data=old.data.copy();ob.name='R33_MAIN_PASSAGE_HIGH_REMAINDER';root.objects.link(ob);ob.hide_render=False;ob.hide_set(False)
for v in ob.data.vertices:
 if v.co.z<.1:v.co.z=TOP
ob['element_id']=ob.name;ob['status']='conditional_high_remainder_above_open_ground_passage';ob['source_ids']='102,PDF2016';ob['assumption_note']='Old schematic lower closure removed below candidate 4.35m; upper appearance remains unresolved.'
for name in made:
 ob=bpy.data.objects[name];ob['zone_id']='GROUND_SERVICES';ob['source_ids']='102,PDF2016';ob['assumption_note']='PDF path 120 centreline interpretation. .25m thickness and 4.35m ceiling unmeasured. No fixture or historical service stair inference.';ob['status']='conditional_plan_service_envelope'
bpy.context.scene['stage']='R33 ground service envelopes from plan';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R33_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R33_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=changed,ceiling_z=TOP,construction_acceptance=False),indent=2),encoding='utf8')
