"""R29 basement gallery enclosures; unlocated finishes remain representative."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/lower_gallery_rooms.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];LOW=json.loads((B/'reports/R05_build_report.json').read_text())['lower_z'];H=LOW+P['clear_height_candidate_m'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R29_ALT_GALERI_MEKAN_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P16_LOWER_GALLERY_ROOMS_REPRESENTATIVE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];up=Vector((0,0,1));white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'];wood=bpy.data.materials['R23_GALLERY_WOOD_FLOOR_CANDIDATE'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE']
def point(x,y,z=0):
 s,dx,dy=C['basement_registration']['source_to_canonical'];x=s*x+dx;y=s*y+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);me=bpy.data.meshes.new(name);me.from_pydata([tuple(p+up*z) for z in [z0,z1] for p in poly],[],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='LM1',zone_id='LOWER_GALLERIES',source_ids=','.join(P['source_ids']),confidence_xy='C source diagram registration',confidence_z='D foyer height extrapolated',confidence_detail='U no located basement photo',status='representative_source_lower_gallery',assumption_note='104 boundary; gallery ceiling/finish/thickness unverified. No exhibition setup copied.').items():o[k]=v
 made.append(name);return o
def wall(name,a,b,center,mat=white):
 a,b=point(*a),point(*b);axis=(b-a).normalized();normal=axis.cross(up)
 if normal.dot((a+b)/2-center)<0:normal=-normal
 return prism(name,[a,b,b+normal*P['wall_thickness_candidate_m'],a+normal*P['wall_thickness_candidate_m']],LOW,H,mat,'gallery_boundary_wall_representative')
for side,coords in P['rooms'].items():
 poly=[point(*p) for p in coords];center=sum(poly,Vector())/len(poly)
 prism('R29_'+side+'_FLOOR',poly,LOW-P['floor_depth_candidate_m'],LOW,wood,'gallery_floor_representative')
 prism('R29_'+side+'_CEILING',poly,H,H+P['ceiling_depth_candidate_m'],white,'gallery_ceiling_representative')
 for i,(a,b) in enumerate(zip(coords,coords[1:]+coords[:1])):
  if side=='E' and i==1:wall('R29_E_FOYER_DIVIDER',a,[420,393],center,stone)
  elif side=='W' and i==len(coords)-1:
   # R07 already supplies the stone divider, aligned with native x623.6.
   wall('R29_W_DIVIDER_END',[623,389.5],[623,393],center,stone)
  else:wall(f'R29_{side}_BOUNDARY_{i:02d}',a,b,center)
prism('R29_FOYER_FLOOR',[point(*p) for p in P['foyer_polygon']],LOW-.2,LOW,stone,'source_foyer_floor_replacement')
old=bpy.data.objects['P05_ZONE_LM1_GALLERIES_FOYER'];old.hide_render=True;old.hide_set(True);changed.append(old.name)
bpy.context.scene['stage']='R29 basement gallery boundary candidates';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R29_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R29_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=changed,lower_z=LOW,ceiling_z=H,construction_acceptance=False),indent=2),encoding='utf8')
