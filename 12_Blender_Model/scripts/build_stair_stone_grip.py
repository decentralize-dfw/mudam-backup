"""R45 photo-supported recessed stone grip, with explicitly candidate profile."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/stair_stone_grip.json').read_text());Q=json.loads((B/'config/upper_stair_flight.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];T=json.loads((B/'reports/R04_build_report.json').read_text());version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R45_TAS_TUTAMAK_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));col=bpy.data.collections.new('R45_RECESSED_STONE_GRIP_CANDIDATE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(col);up=Vector((0,0,1));mat=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];A=P['start_sum_canonical'];E=P['end_sum_canonical'];scale=C['meters_per_canonical_pixel'];LOW=T['podium_level'];UP=T['upper_level']
def xy(p):
 k=C['canonical_to_pdf_scale'];o=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*p[0]+o[0];b=k*p[1]+o[1];return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
def outer(s):
 a,b,c,d=Q['wall_bezier_canonical']
 def f(t):return [(1-t)**3*a[i]+3*(1-t)**2*t*b[i]+3*(1-t)*t*t*c[i]+t**3*d[i] for i in range(2)]
 if s>sum(d):return [d[i]+(s-sum(d))*(d[i]-c[i])/sum(d[j]-c[j] for j in range(2)) for i in range(2)]
 lo,hi=0.,1.
 for _ in range(50):
  m=(lo+hi)/2
  if sum(f(m))<s:lo=m
  else:hi=m
 return f((lo+hi)/2)
def ramp(s):return LOW+(UP-LOW)*(s-Q['start_sum_canonical'])/(Q['landing_sum_canonical']-Q['start_sum_canonical'])
def normal(s):
 p=xy(outer(s));tan=(xy(outer(s+.001))-xy(outer(s-.001))).normalized();n=up.cross(tan);target=xy([(s+T['tread_d'])/2,(s-T['tread_d'])/2])-p;return n if n.dot(target)>0 else -n
def point(s,z,depth):return xy(outer(s))+normal(s)*depth+up*z
def mesh(name,verts,faces,hidden=False):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat);ob.hide_render=hidden;ob.hide_set(hidden);ob['source_ids']=','.join(P['source_ids']);ob['confidence_detail']='D candidate dimensions, photographed form';ob['parameter_ids']='stair_stone_grip.json';ob['assumption_note']='Recess shape observed in024; profile and full extent unmeasured';ob['element_id']=name;return ob
# The capsule is parameterized by the existing wall's arc length.
ss=[A+(E-A)*i/256 for i in range(257)];dist=[0.]
for a,b in zip(ss,ss[1:]):dist.append(dist[-1]+(xy(outer(b))-xy(outer(a))).length)
length=dist[-1];radius=P['cavity_height_m']/2
def s_at(t):
 for i in range(256):
  if dist[i+1]>=t:return ss[i]+(ss[i+1]-ss[i])*(t-dist[i])/(dist[i+1]-dist[i])
 return E
# Include round-end stations and central wall subdivisions, no zero-length caps.
xs=sorted(set([0.,length]+[radius*(1-math.cos(math.pi*j/32)) for j in range(1,17)]+[length-radius*(1-math.cos(math.pi*j/32)) for j in range(1,17)]+[radius+(length-2*radius)*i/160 for i in range(161)]))
def halfwidth(x):
 if x<radius:return math.sqrt(max(0,radius**2-(x-radius)**2))
 if x>length-radius:return math.sqrt(max(0,radius**2-(x-(length-radius))**2))
 return radius
profile=[(x,halfwidth(x)) for x in xs]+[(x,-halfwidth(x)) for x in reversed(xs[1:-1])];n=len(profile);nx=len(xs)
def lowidx(i):return i if i in [0,nx-1] else n-i
frontfaces=[]
for i in range(nx-1):
 face=list(dict.fromkeys([i,i+1,lowidx(i+1),lowidx(i)]));frontfaces.append(tuple(face))
faces=frontfaces+[tuple(j+n for j in reversed(f)) for f in frontfaces]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];verts=[tuple(point(s_at(x),ramp(s_at(x))+P['cavity_center_above_ramp_m']+z,d)) for d in [.025,-P['cavity_depth_m']] for x,z in profile];cut=mesh('R45_RECESS_BOOLEAN_CANDIDATE',verts,faces,True);cut.display_type='WIRE';changed=[];volumes=[]
def volume(me):
 bm=bmesh.new();bm.from_mesh(me);v=abs(bm.calc_volume(signed=True));bm.free();return v
# Stitch the inherited 64 wall pieces into a continuous finish shell.
# Front chain points are copied in world coordinates, not retraced.
legacy=[bpy.data.objects[f'R04_RECESS_BACK_{i:02}'] for i in range(64)];front=[];back=[];head=T['recess_head'];front_error=0.
for i,ob in enumerate(legacy):
 vs=[ob.matrix_world@v.co for v in ob.data.vertices]
 if i==0:front.append(vs[0]);back.append(vs[3])
 else:
  front_error=max(front_error,(front[-1]-vs[0]).length);back[-1]=(back[-1]+vs[3])/2
 front.append(vs[1]);back.append(vs[2])
 ob.hide_render=True;ob.hide_set(True);ob['detail_superseded_by']='R45_STAIR_RECESS_CONTINUOUS';changed.append(ob.name)
assert front_error<.00002,front_error
nwall=len(front);wallverts=[tuple(Vector((p.x,p.y,z))) for z in [0,head] for chain in [front,back] for p in chain];wallfaces=[]
for i in range(nwall-1):
 j=i+1;wallfaces += [(i,j,j+2*nwall,i+2*nwall),(i+nwall,i+3*nwall,j+3*nwall,j+nwall),(i,i+nwall,j+nwall,j),(i+2*nwall,j+2*nwall,j+3*nwall,i+3*nwall)]
wallfaces += [(0,2*nwall,3*nwall,nwall),(nwall-1,2*nwall-1,4*nwall-1,3*nwall-1)]
wall=mesh('R45_STAIR_RECESS_CONTINUOUS',wallverts,wallfaces);wall['front_chain_preserved_m']=front_error;before=volume(wall.data);bpy.context.view_layer.objects.active=wall;mod=wall.modifiers.new('R45 photographed stone grip recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);volumes.append(dict(name=wall.name,before=before,after=volume(wall.data)))
# The floor previously terminated 20mm inside this wall. Reserve the cavity
# through that hidden finish overlap too; no change to the walking surface.
floorcut=mesh('R45_FLOOR_RECESS_NUMERICAL_RESERVE',[tuple(point(s_at(x),ramp(s_at(x))+P['cavity_center_above_ramp_m']+z+(0.005 if z>0 else -0.005 if z<0 else 0),d)) for d in [.045,-P['cavity_depth_m']-.02] for x,z in profile],faces,True);floorcut['purpose']='20mm extra depth removes coplanar floor/recess surface, not an architectural dimension'
floor=bpy.data.objects['P05_FLOOR_LP1_BRIDGE'];mod=floor.modifiers.new('R45 stone recess local floor overlap','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=floorcut;changed.append(floor.name)
# Rounded top corners of the stone lip; bottom joins the recess sill.
grip_front=P['stone_grip_projection_m'];back=-.07;height=P['stone_grip_height_m'];bevel=.012;cross=[(back,0),(grip_front,0),(grip_front,height-bevel),(grip_front-bevel*.293,height-bevel*.293),(grip_front-bevel,height),(back+bevel,height),(back+bevel*.293,height-bevel*.293),(back,height-bevel)];grip_ss=[s_at(P['stone_grip_end_inset_m']+(length-2*P['stone_grip_end_inset_m'])*i/160) for i in range(161)];gverts=[tuple(point(s,ramp(s)+P['cavity_center_above_ramp_m']-radius+z,d)) for s in grip_ss for d,z in cross];k=len(cross);gfaces=[tuple(range(k-1,-1,-1)),tuple(range((len(grip_ss)-1)*k,len(grip_ss)*k))]+[(i*k+j,i*k+(j+1)%k,(i+1)*k+(j+1)%k,(i+1)*k+j) for i in range(len(grip_ss)-1) for j in range(k)];grip=mesh('R45_STONE_GRIP_FINISH_CANDIDATE',gverts,gfaces);grip['element_type']='recessed stone grip finish';grip['upper_termination_verified']=False
samples=[]
for i in range(1,40):
 s=s_at(radius+(length-2*radius)*i/40);z=ramp(s)+P['cavity_center_above_ramp_m'];samples.append(dict(s=s,front=list(point(s,z,.02)),recess_back=list(point(s,z,-P['cavity_depth_m'])),outside=list(point(s,z,-.2)),normal=list(normal(s))))
bpy.context.scene['stage']='R45 recessed stone grip candidate';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R45_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=[wall.name,grip.name,floor.name],front_chain_world=[list(p) for p in front],front_chain_join_error_m=front_error,changed_inherited_objects=changed,volumes=volumes,cavity_samples=samples,cavity_length_m=length,candidate_dimensions=P,construction_acceptance=False);(B/'reports/R45_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');m=json.loads((B/'references/source_manifest.json').read_text(encoding='utf8'));sources=[x for x in m if x['id'] in P['source_ids']]
for x in sources:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
(B/'reports/R45_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=P['limits']),ensure_ascii=False,indent=2),encoding='utf8');print('R45_SAVED',out,len(changed))
