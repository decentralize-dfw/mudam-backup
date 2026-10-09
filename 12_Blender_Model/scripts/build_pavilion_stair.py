"""R25 explicitly representative pavilion spiral, stone guard and lower floor."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/pavilion_stair.json').read_text());ROOM=json.loads((B/'config/pavilion_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];ref=json.loads((B/'reports/R17_build_report.json').read_text());LOW=ref['lower_floor_z'];outer=ref['stair_radius'];inner=P['inner_radius_m'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R25_PAVYON_MERDIVEN_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P09_PAVILION_STAIR_REPRESENTATIVE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];up=Vector((0,0,1));stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];floor=bpy.data.materials['P05_FLOOR_REFERENCE'];metal=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE'];steps=[]
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
center=point(*ROOM['stair_center_canonical']);ax=(point(73.5,269)-center).normalized();ay=(point(72.5,270)-center).normalized()
def radial(a,r,z):return center+(ax*math.cos(a)+ay*math.sin(a))*r+up*z
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='PAV',level_id='L00_LM1_PAV',source_ids=','.join(P['source_ids']),confidence_xy='C plan circle; D entrance candidate',confidence_z='D section ratio',confidence_detail='D representative not measured',status='representative_pavilion_stair',assumption_note='24 risers / 360 degrees / handedness / entrances unverified; do not treat as reconstructed measured staircase.').items():ob[k]=v
 made.append(name);return ob
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);return mesh(name,[p+up*z for z in [z0,z1] for p in poly],[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,kind)
def band(name,a0,a1,r0,r1,z0,z1,n,mat,kind):
 vs=[]
 for i in range(n+1):
  f=i/n;a=a0+(a1-a0)*f;lo=z0(f) if callable(z0) else z0;hi=z1(f) if callable(z1) else z1;vs.extend([radial(a,r0,lo),radial(a,r1,lo),radial(a,r1,hi),radial(a,r0,hi)])
 fs=[]
 for i in range(n):
  for j in range(4):fs.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
 fs.extend([(3,2,1,0),(4*n,4*n+1,4*n+2,4*n+3)]);ob=mesh(name,vs,fs,mat,kind)
 for i in range(n):
  for j in [1,3]:ob.data.polygons[4*i+j].use_smooth=True
 return ob
prism('R25_LOWER_PAVILION_FLOOR',[point(*p) for p in ROOM['footprint']],LOW-.2,LOW,floor,'lower_pavilion_floor_candidate')
start=math.radians(P['start_angle_canonical_degrees']);turn=math.radians(P['turn_degrees']);count=P['risers'];rise=-LOW/count;da=turn/count
for i in range(count):
 a0=start+i*da;a1=a0+da;z=-(i+1)*rise;ob=band(f'R25_TREAD_{i+1:02d}',a0,a1,inner,outer,z-P['step_underside_m'],z,8,stone,'stone_wedge_tread_candidate');steps.append(dict(name=ob.name,angle=[a0,a1],z=z,index=i+1))
band('R25_UPPER_LANDING',math.radians(P['landing_start_degrees']),start,inner,outer+.02,-.2,0,24,stone,'upper_landing_candidate')
# Central core closes the plan's inner circle. No glass railing inferred.
core=[radial(math.tau*i/96,inner,0) for i in range(96)];prism('R25_STONE_CORE',core,LOW,.95,stone,'stone_core_candidate')
band('R25_GROUND_PARAPET',start,math.tau+math.radians(P['landing_start_degrees']),outer,outer+P['parapet_thickness_m'],0,P['parapet_height_m'],168,stone,'stone_floor_guard_candidate')
band('R25_HELICAL_OUTER_GUARD',start,start+turn,outer,outer+P['parapet_thickness_m'],lambda f:LOW*f-P['step_underside_m'],lambda f:LOW*f+P['parapet_height_m'],192,stone,'stone_helical_guard_candidate')
guard=bpy.data.objects['R25_HELICAL_OUTER_GUARD'];operand=bpy.data.objects['R25_GROUND_PARAPET'];mod=guard.modifiers.new('Union floor parapet and descending stone guard','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=operand;operand.hide_render=True;operand.hide_set(True)
# Round wall rail seen descending beside the parapet; geometry is a candidate.
vs=[];fs=[];nr=12;np=193;rad=outer-.09
for i in range(np):
 f=i/(np-1);a=start+turn*f;p=radial(a,rad,LOW*f+.86);normal=(ax*math.cos(a)+ay*math.sin(a));tangent=(-ax*math.sin(a)+ay*math.cos(a))*rad*turn+up*LOW;tangent.normalize();side=tangent.cross(normal).normalized()
 for j in range(nr):vs.append(p+(normal*math.cos(j*math.tau/nr)+side*math.sin(j*math.tau/nr))*P['handrail_diameter_m']/2)
for i in range(np-1):
 for j in range(nr):fs.append((i*nr+j,i*nr+(j+1)%nr,(i+1)*nr+(j+1)%nr,(i+1)*nr+j))
fs.extend([tuple(range(nr-1,-1,-1)),tuple((np-1)*nr+j for j in range(nr))]);mesh('R25_WALL_HANDRAIL',vs,fs,metal,'round_handrail_candidate')
for j in range(8):
 f=(j+.5)/8;a=start+turn*f;p=radial(a,rad,LOW*f+.86);q=radial(a,outer+.015,LOW*f+.86);axis=(q-p).normalized();u=axis.cross(up).normalized();v=axis.cross(u).normalized();ring=[(u*math.cos(k*math.tau/12)+v*math.sin(k*math.tau/12))*.009 for k in range(12)];verts=[c+d for c in [p,q] for d in ring];faces=[tuple(range(11,-1,-1)),tuple(range(12,24))]+[(k,(k+1)%12,(k+1)%12+12,k+12) for k in range(12)];mesh(f'R25_RAIL_BRACKET_{j:02d}',verts,faces,metal,'representative_wall_rail_bracket')
bpy.context.scene['stage']='R25 pavilion representative spiral; unverified handedness/count';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R25_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R25_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[],steps=steps,center=list(center),axis_x=list(ax),axis_y=list(ay),inner_radius=inner,outer_radius=outer,lower_z=LOW,rise=rise,construction_acceptance=False),indent=2),encoding='utf8')
