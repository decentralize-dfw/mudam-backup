"""R31 source-supported detached entrance walls and gallery finish candidates."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/upper_studio.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R31_UST_STUDIO_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P17_UPPER_STUDIO_REPRESENTATIVE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];up=Vector((0,0,1));white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'];wood=bpy.data.materials['R23_GALLERY_WOOD_FLOOR_CANDIDATE'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE']
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);vs=[tuple(p+up*z) for z in [z0,z1] for p in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='LP1',zone_id='UPPER_STUDIO',source_ids=','.join(P['source_ids']),confidence_xy='C diagram topology; thickness conditional',confidence_z='D candidate',confidence_detail='D unmeasured',status='representative_source_studio',assumption_note='Studio ceiling inherited from reading-room candidate; interior photo not located.').items():o[k]=v
 made.append(name);return o
UP=json.loads((B/'reports/R09_build_report.json').read_text())['floor_z'];TOP=P['ceiling_z'];HEAD=UP+P['portal_head_candidate_m'];poly=[point(*p) for p in P['inner_polygon']];center=sum(poly,Vector())/len(poly)
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 axis=(b-a).normalized();normal=axis.cross(up)
 if normal.dot((a+b)/2-center)<0:normal=-normal
 def wall(name,p,q,z0,z1):return prism(name,[p,q,q+normal*P['wall_thickness_candidate_m'],p+normal*P['wall_thickness_candidate_m']],z0,z1,white,'studio_wall_envelope_candidate')
 if i==1:
  p,q=[point(528.77,y) for y in P['portal_range_y']];wall('R31_EAST_JAMB_A',a,p,UP,TOP);wall('R31_EAST_JAMB_B',q,b,UP,TOP);wall('R31_EAST_HEAD',p,q,HEAD,TOP)
 else:wall('R31_STUDIO_WALL_'+str(i),a,b,UP,TOP)
prism('R31_STUDIO_CEILING',poly,TOP,TOP+.18,white,'studio_ceiling_representative')
y0,y1=P['portal_range_y'];x0=528.77;x1=P['portal_end_x'];p=[point(x,y) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];prism('R31_PASSAGE_CEILING',p,HEAD,TOP,stone,'studio_reading_passage_head_candidate')
for label,y,direction in [('N',y0,-1),('S',y1,1)]:
 a,b=point(x0,y),point(x1,y);ey=(point(0,1)-point(0,0)).normalized()*direction*.3;prism('R31_PASSAGE_SIDE_'+label,[a,b,b+ey,a+ey],UP,HEAD,stone,'studio_reading_passage_side_candidate')
bpy.context.scene['stage']='R31 upper Studio perimeter and reading-room link';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R31_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R31_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[],upper_z=UP,ceiling_z=TOP,construction_acceptance=False),indent=2),encoding='utf8')
