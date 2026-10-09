"""R23 six-sided upper galleries, source gaps and corrected west return passage."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/upper_gallery_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};UP=Z['Z_LP1_FINISH'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R23_UST_GALERI_MEKAN_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P17_UPPER_GALLERY_ROOMS_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];portals=[];up=Vector((0,0,1));white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];wood=bpy.data.materials.new('R23_GALLERY_WOOD_FLOOR_CANDIDATE');wood.use_nodes=True;wood.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.25,.15,.065,1);wood.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.52
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='UPPER_GALLERIES',level_id='LP1',source_ids='103,PDF2016,UG02,UG03,UC01,UC02',confidence_xy='C source polygon/gaps; D projection/jamb detail',confidence_z='D section and architect description',confidence_detail='D unmeasured',status='conditional_upper_gallery_room',assumption_note='Door gaps from PDF; heads and wall thickness candidates. Existing five-bay roof remains provisional.').items():ob[k]=v
 made.append(name);return ob
def prism(name,poly,z0,z1,mat,kind):
 N=len(poly);return mesh(name,[p+up*z for z in [z0,z1] for p in poly],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],mat,kind)
for side,coords in P['source_polygons_canonical'].items():
 poly=[point(*p) for p in coords];center=sum(poly,Vector())/len(poly)
 for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  axis=(b-a).normalized();normal=axis.cross(up)
  if normal.dot((a+b)/2-center)<0:normal=-normal
  th=P['wall_display_thickness_m'];spec=next((p for p in P['portals'] if p['side']==side and p['edge']==i),None)
  def wall(name,p,q,z0,z1):return prism(name,[p,q,q+normal*th,p+normal*th],z0,z1,white,'upper_gallery_finish_wall_candidate')
  if spec:
   distances=sorted((point(*p)-a).dot(axis) for p in spec['ends']);lo,hi=[max(0,min((b-a).length,d)) for d in distances];p=a+axis*lo;q=a+axis*hi
   wall(f'R23_{side}_{i}_JAMB_A',a,p,UP,P['wall_top_z']);wall(f'R23_{side}_{i}_JAMB_B',q,b,UP,P['wall_top_z']);wall(f'R23_{side}_{i}_HEAD',p,q,UP+spec['head'],P['wall_top_z']);portals.append(dict(id=spec['id'],start=list(p),end=list(q),outward=list(normal),head_above_floor=spec['head'],projection_residual_m=[abs((point(*src)-a).dot(normal)) for src in spec['ends']]))
   prism('R23_THRESHOLD_'+spec['id'],[p-normal*.15,q-normal*.15,q+normal*1.0,p+normal*1.0],UP-.2,UP,stone,'source_portal_floor_connection_candidate')
  else:wall(f'R23_{side}_{i}_WALL',a,b,UP,P['wall_top_z'])
 floor=bpy.data.objects[f'P05_FLOOR_LP1_{side}0'];floor.data.materials.clear();floor.data.materials.append(wood);changed.append(floor.name)
for i,poly in enumerate(P['west_return_uv']):
 pts=[point((u+v)/2,(u-v)/2) for u,v in poly];prism(f'R23_WEST_RETURN_FLOOR_{i}',pts,UP-.2,UP,stone,'source_west_return_passage_candidate')
bpy.context.scene['stage']='R23 upper gallery room candidates and source west return route';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R23_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=changed,portals=portals,upper_z=UP,old_west_straight_route_superseded=True,construction_acceptance=False);(B/'reports/R23_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
