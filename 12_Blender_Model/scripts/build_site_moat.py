"""R35 source-supported detached entrance walls and gallery finish candidates."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/site_moat.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R35_HENDEK_CEVRE_ETUDU_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P18_MOAT_HISTORIC_WALL_CONTEXT');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];up=Vector((0,0,1));white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'];wood=bpy.data.materials['R23_GALLERY_WOOD_FLOOR_CANDIDATE'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE']
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);vs=[tuple(p+up*z) for z in [z0,z1] for p in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='SITE',zone_id='GROUND_SERVICES',source_ids=','.join(P['source_ids']),confidence_xy='C diagram topology; thickness conditional',confidence_z='D candidate',confidence_detail='D unmeasured',status='conditional_plan_service_envelope',assumption_note='Source wall centreline interpretation; thickness, head and finishes unmeasured.').items():o[k]=v
 made.append(name);return o
sys.path.insert(0,str(Path(__file__).parent));from plan_union import inside,cross,sub
Q=json.loads((B/'reports/R34_build_report.json').read_text());deckpoly=Q['union_boundary'];walls=[]
def mat(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=.88;return m
historic=mat('R35_HISTORIC_WALL_UNTEXTURED_CONTEXT',(.24,.18,.12));grass=mat('R35_MOAT_GROUND_CONTEXT',(.12,.17,.075))
prism('R35_MOAT_GROUND',[Vector((*p,0)) for p in P['moat_polygon']],P['moat_z_candidate']-.25,P['moat_z_candidate'],grass,'flat_moat_ground_unmeasured')
for path in P['wall_paths']:
 ps=[Vector((*p,0)) for p in path['points']];normals=[up.cross((b-a).normalized()) for a,b in zip(ps,ps[1:])];offsets=[]
 for i in range(len(ps)):
  if i==0:n=normals[0]
  elif i==len(ps)-1:n=normals[-1]
  else:
   n=(normals[i-1]+normals[i]).normalized();n/=max(.2,n.dot(normals[i]))
  offsets.append(n*P['wall_width_candidate_m']/2)
 for i,(a,b) in enumerate(zip(ps,ps[1:])):
  av=list(a)[:2];v=list(b-a)[:2];ts=[0.,1.]
  for c,d in zip(deckpoly,deckpoly[1:]+deckpoly[:1]):
   w=sub(d,c);den=cross(v,w)
   if abs(den)>1e-9:
    t=cross(sub(c,av),w)/den;u=cross(sub(c,av),v)/den
    if 1e-7<t<1-1e-7 and 0<=u<=1:ts.append(t)
  ts=sorted(set(ts))
  for j,(t0,t1) in enumerate(zip(ts,ts[1:])):
   mid=a.lerp(b,(t0+t1)/2);top=P['inner_top_candidate'] if path['role']=='inner' else P['outer_top_candidate'];under_bridge=inside(list(mid)[:2],deckpoly)
   if under_bridge:top=min(top,-.40)
   left0=(a-offsets[i]).lerp(b-offsets[i+1],t0);left1=(a-offsets[i]).lerp(b-offsets[i+1],t1);right0=(a+offsets[i]).lerp(b+offsets[i+1],t0);right1=(a+offsets[i]).lerp(b+offsets[i+1],t1);name=f"R35_WALL_{path['id']}_{i:02d}_{j}"
   prism(name,[left0,left1,right1,right0],P['wall_base_candidate'],top,historic,'historic_wall_context_not_detailed');walls.append(dict(name=name,way=path['id'],segment=i,range=[t0,t1],top=top,under_bridge=under_bridge,center=list(mid)))
for name in made:
 ob=bpy.data.objects[name];ob['source_ids']='063,065,096,116,OSM';ob['zone_id']='MOAT_NORTH_EAST';ob['confidence_xy']='C OSM wall paths; terrain interpretation D';ob['confidence_z']='D flat moat and wall top candidates';ob['assumption_note']='Context volume only. No surveyed height, stone texture, ruin opening, drainage or foundation detail.';ob['status']='representative_site_context'
bpy.context.scene['stage']='R35 first moat and historic wall context';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R35_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R35_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[],walls=walls,ground_z=P['moat_z_candidate'],construction_acceptance=False),indent=2),encoding='utf8')
