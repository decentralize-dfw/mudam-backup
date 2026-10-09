"""R26 photograph-supported glazed strip between east roof and gallery wall."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(Path(__file__).parent));from roof_panel_math import inset
P=json.loads((B/'config/east_roof_strip.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];H=json.loads((B/'config/entry_package.json').read_text())['lower_roof']['band_bottom_z'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R26_DOGU_CATI_BAGLANTI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P11_EAST_ROOF_STRIP_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE'];up=Vector((0,0,1));made=[];panels=[];frames=[];keys=set()
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def solid(name,ps,n,depth,mat,kind):
 N=len(ps);vs=ps+[p-n*depth for p in ps];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];me=bpy.data.meshes.new(name);me.from_pydata([tuple(p) for p in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='EAST_GARDEN_ROOF_STRIP',level_id='ROOF',source_ids=','.join(P['source_ids']),confidence_xy='C existing plan boundaries',confidence_z='D inherited roof edge',confidence_detail='D horizontal strip and module candidate',status='conditional_roof_strip',assumption_note='033/034 show framed glass strip; exact fall, member sections, drainage and panel counts unmeasured.').items():ob[k]=v
 made.append(name);return ob
def frame(a,b,width=None,depth=None,label='FRAME'):
 key=tuple(sorted(tuple(round(v,6) for v in p) for p in [a,b]))
 if key in keys:return
 keys.add(key);side=up.cross((b-a).normalized())*(width or P['frame_width_m'])/2;lift=up*.025;ob=solid(f'R26_{label}_{len(frames):03d}',[a-side+lift,b-side+lift,b+side+lift,a+side+lift],up,depth or P['frame_depth_m'],metal,'glazed_strip_frame_candidate');frames.append(ob.name)
def low(x):return 266.5+(x-289.5)*(441.1-266.5)/(462.4-289.5)
def high(x):return 347.3+max(0,x-349)
def at(x,v):return point(x,low(x)*(1-v)+high(x)*v,H)
xs=sorted(set([289.5+(462.4-289.5)*i/P['columns_candidate'] for i in range(P['columns_candidate']+1)]+[349.0]))
for i,(x0,x1) in enumerate(zip(xs,xs[1:])):
 for j in range(P['rows_candidate']):
  v0=j/P['rows_candidate'];v1=(j+1)/P['rows_candidate'];ps=[at(x0,v0),at(x1,v0),at(x1,v1),at(x0,v1)];ip=inset([[p.x,p.y] for p in ps],P['frame_width_m']/2);assert len(ip)>=3
  name=f'R26_GLASS_{i:02d}_{j:02d}';solid(name,[Vector((x,y,H)) for x,y in ip],up,P['glass_thickness_m'],glass,'flat_roof_strip_glass_candidate');panels.append(dict(name=name,center=list(sum(ps,Vector())/4),corners=[list(p) for p in ps]))
  for a,b in zip(ps,ps[1:]+ps[:1]):frame(a,b)
# Deeper visible head along the gallery side, as in 033. No hidden connector invented.
for x0,x1 in zip(xs,xs[1:]):
 a=at(x0,1);b=at(x1,1);side=up.cross((b-a).normalized())*P['wall_edge_beam_width_m']/2;solid(f'R26_WALL_HEAD_{x0:.3f}',[a-side,b-side,b+side,a+side],up,P['wall_edge_beam_depth_m'],metal,'visible_wall_edge_head_candidate')
bpy.context.scene['stage']='R26 glazed east roof-to-gallery strip candidate';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R26_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R26_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,panels=panels,frames=frames,changed_inherited_objects=[],z=H,outline_canonical=[[289.5,266.5],[462.4,441.1],[462.4,460.7],[349,347.3],[289.5,347.3]],construction_acceptance=False),indent=2),encoding='utf8')
