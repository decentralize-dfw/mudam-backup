"""R34 OSM bridge footprints, entrance continuity and candidate edge protection."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/site_bridges.json').read_text());version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R34_GIRIS_KOPRULERI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P18_OSM_APPROACH_BRIDGES_CANDIDATE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];up=Vector((0,0,1));ways={w['id']:w for w in P['ways']};stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];floor=bpy.data.materials['P05_FLOOR_REFERENCE'];metal=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE'];ashlar=bpy.data.materials['R32_LIMESTONE_APPEARANCE_CANDIDATE']
def points(id):
 ps=[Vector((x-293425,y-5499960,0)) for x,y in ways[id]['xy']]
 return ps[:-1] if (ps[0]-ps[-1]).length<1e-5 else ps

def tag(ob,source,kind):
 for k,v in dict(element_id=ob.name,element_type=kind,level_id='L00_APPROACH',zone_id='APPROACH',source_ids=source,confidence_xy='C OSM footprint, same building CRS',confidence_z='D entrance-zero candidate',confidence_detail='D profile and thickness assumptions',status='conditional_osm_bridge_candidate',assumption_note='No bridge fall, structural support, member section or historic height claimed as measured.').items():ob[k]=v
 made.append(ob.name);return ob

def mesh(name,vs,fs,mat,source,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat);return tag(ob,source,kind)

def prism(name,poly,z0,z1,mat,source,kind):
 n=len(poly);return mesh(name,[tuple(p+up*z) for z in [z0,z1] for p in poly],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,source,kind)

def bar(name,a,b,width,z0,z1,mat,source,inward=None):
 normal=up.cross((b-a).normalized())
 if inward is not None:
  if normal.dot(inward-(a+b)/2)<0:normal=-normal
  ps=[a,b,b+normal*width,a+normal*width]
 else:ps=[a-normal*width/2,b-normal*width/2,b+normal*width/2,a+normal*width/2]
 return prism(name,ps,z0,z1,mat,source,'bridge_edge_member_candidate')

def tube(name,a,b,radius,source):
 axis=(b-a).normalized();u=axis.cross(up)
 if u.length<.1:u=Vector((1,0,0))
 u.normalize();v=axis.cross(u);N=12;vs=[tuple(c+(u*math.cos(i*2*math.pi/N)+v*math.sin(i*2*math.pi/N))*radius) for c in [a,b] for i in range(N)];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];return mesh(name,vs,fs,metal,source,'bridge_handrail_candidate')
sys.path.insert(0,str(Path(__file__).parent));from plan_union import union
C=json.loads((B/'config/foundation.json').read_text())['calibration'];E=json.loads((B/'config/entry_package.json').read_text())['entry']
def xy(p):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return [M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960]
old=bpy.data.objects['P07_CANOPY_PAVING_DISPLAY'];old_outline=[xy(p) for p in E['chain']+[E['roof_triangle'][1]]]
polys=[old_outline,[[p.x,p.y] for p in [points('759551375')[0],points('759551375')[-1],points('759551376')[0]]]]+[[[p.x,p.y] for p in points(id)] for id in ['759551375','759551376']]
loops=union(polys);assert len(loops)==1,'Unexpected holes or disconnected paving';ob=prism('R34_APPROACH_CONTINUOUS_DECK',[Vector((*p,0)) for p in loops[0]],-P['deck_thickness_m'],0,floor,'OSM759551375,OSM759551376,102,116','united_approach_deck_candidate');old.hide_render=True;old.hide_set(True)
for wall,bridge in [('759554469','759551375'),('759554471','759551376')]:
 a,b=points(wall);center=sum(points(bridge),Vector())/len(points(bridge));o=bar('R34_STONE_PARAPET_'+wall,a,b,P['parapet_width_m'],0,P['parapet_height_m'],stone,'OSM'+wall+',063,116',center);o.data.materials.append(ashlar);uv=o.data.uv_layers.new(name='R32_METRIC_SURFACE_UV')
 for face in o.data.polygons:
  n=face.normal
  if abs(n.z)>.05:continue
  face.material_index=1;u=Vector((-n.y,n.x,0));u=-u if u.x<0 else u
  for li in face.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/3.2,p.z/2.4)
for rail in ['759554470','759554472']:
 a,b=points(rail);count=math.ceil((b-a).length/P['post_pitch_max_m']);h=P['handrail_height_m']
 for i in range(count+1):
  c=a.lerp(b,i/count);tube(f'R34_POST_{rail}_{i:02d}',c+up*.02,c+up*h,P['post_width_m']/2,'OSM'+rail+',116')
 for j,z in enumerate([.35,.70,h]):tube(f'R34_RAIL_{rail}_{j}',a+up*z,b+up*z,P['rail_radius_m'],'OSM'+rail+',116')
bpy.context.scene['stage']='R34 mapped bridge approach with candidate rails';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R34_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R34_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[old.name],deck=ob.name,original_paving_outline=old_outline,union_boundary=loops[0],osm_footprints={id:[list(p)[:2] for p in points(id)] for id in ['759551375','759551376']},routes={'NORTH':[[29,62],[29,36]],'EAST':[[57,33],[30,33]]},construction_acceptance=False),indent=2),encoding='utf8')
