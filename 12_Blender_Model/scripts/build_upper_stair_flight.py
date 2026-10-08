"""R04: conditional complete GH upward stair, photo-supported recess and guard."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/upper_stair_flight.json').read_text());Q=json.loads((B/'config/stair_glass_return.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']}
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R04_UST_MERDIVEN_{version}.blend'
if out.exists():raise RuntimeError('Choose new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('P09_GH_UP_FULL_FLIGHT_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];made=[];cutters=[];replaced=[];up=Vector((0,0,1));UP=Z['Z_LP1_FINISH'];LOW=json.loads((B/'config/stair_podium.json').read_text())['draft_podium_top_z'];scale=C['meters_per_canonical_pixel']
def xy(p):
 k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+off[0];v=k*p[1]+off[1]
 return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
def sd(s,d):return [(s+d)/2,(s-d)/2]
def at(s,d,z):return xy(sd(s,d))+up*z
axis=(xy([501,501])-xy([500,500])).normalized();normal=(xy([501,499])-xy([500,500])).normalized();center=xy(Q['center_canonical']);start=center+normal*Q['radius_m'];guard_d=Q['center_canonical'][0]-Q['center_canonical'][1]+math.sqrt(2)*Q['radius_m']/scale;return_s=sum(Q['center_canonical']);tread_d=guard_d-math.sqrt(2)*P['tread_inset_from_glass_m']/scale
A=P['start_sum_canonical'];E=P['landing_sum_canonical'];L=P['landing_end_sum_canonical'];N=P['main_risers_candidate'];pitch=(E-A)/(N-1);rise=(UP-LOW)/N;W=P['recess_start_sum_canonical'];GH=Q['rail_height_above_podium_m'];head=UP+P['recess_head_above_upper_floor_m']
def height(s):return LOW+(UP-LOW)*max(0,min(1,(s-A)/(E-A)))
def outer(s):
 a,b,c,d=P['wall_bezier_canonical']
 def point(t):return [(1-t)**3*a[i]+3*(1-t)**2*t*b[i]+3*(1-t)*t*t*c[i]+t**3*d[i] for i in range(2)]
 if s>sum(d):
  v=[d[i]-c[i] for i in range(2)];t=(s-sum(d))/sum(v);return [d[i]+t*v[i] for i in range(2)]
 lo=0.;hi=1.
 for _ in range(50):
  mid=(lo+hi)/2
  if sum(point(mid))<s:lo=mid
  else:hi=mid
 return point((lo+hi)/2)
def mesh(name,verts,faces,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='GH_UP',level_id='MULTI',source_ids=','.join(P['source_ids']),source_date='see source manifest',permanent_or_temporary='candidate_permanent',confidence_xy='C lower trace / D upper extension',confidence_z='D conditional section level',confidence_detail='D geometric hypothesis',confidence_material='D neutral photo-family material',parameter_ids='upper_stair_flight.json;stair_glass_return.json',assumption_note='Complete-flight candidate. Riser count, upper tangent extension and opening dimensions are not measured. No structural or survey acceptance.',status='conditional_complete_flight_candidate',visibility_group='GH_UP',export_group='R04_CANDIDATE',collision_role='review_only').items():ob[k]=v
 made.append(name);return ob
def prism(name,poly,z0,z1,mat,kind):
 # The upper extrapolated curve is straight: remove collinear samples before
 # tessellation so they cannot become degenerate triangles at its transition.
 poly=[list(p) for p in poly]
 while len(poly)>3:
  remove=None
  for j,b in enumerate(poly):
   a=poly[j-1];c=poly[(j+1)%len(poly)];cross=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
   if abs(cross)<1e-6:remove=j;break
  if remove is None:break
  poly.pop(remove)
 points=[xy(p) for p in poly];n=len(points);lookup={tuple(p):i for i,p in enumerate(points)}
 def idx(v):return v if isinstance(v,int) else lookup[tuple(v)]
 tris=tessellate_polygon([points]);faces=[tuple(idx(v) for v in reversed(t)) for t in tris]+[tuple(idx(v)+n for v in t) for t in tris]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,[tuple(p+up*z) for z in [z0,z1] for p in points],faces,mat,kind)
def rail_band(name,s0,s1,d0,d1,zbot0,zbot1,ztop0,ztop1,mat,kind):
 verts=[at(s,d,z) for s,zbot,ztop in [(s0,zbot0,ztop0),(s1,zbot1,ztop1)] for z in [zbot,ztop] for d in [d0,d1]]
 return mesh(name,list(map(tuple,verts)),[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],mat,kind)
def tube(name,a,b,diam):
 direct=(b-a).normalized();u=direct.cross(normal).normalized()*diam/2;v=direct.cross(u).normalized()*diam/2;n=16;ring=[u*math.cos(j*math.tau/n)+v*math.sin(j*math.tau/n) for j in range(n)]
 return mesh(name,[tuple(p+q) for p in [a,b] for q in ring],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)],metal,'round_guard_handrail_candidate')
steps=[]
for i in range(N):
 s0=A+i*pitch;s1=s0+pitch if i<N-1 else L;top=LOW+(i+1)*rise
 poly=[outer(s0+(s1-s0)*j/8) for j in range(9)]+[sd(s1,tread_d),sd(s0,tread_d)]
 ob=prism(f'R04_TREAD_ENVELOPE_{i+1:02}',poly,LOW,top,stone,'stair_finish_mass_envelope_not_structure');ob['riser_index_candidate']=i+1
 steps.append(dict(name=ob.name,s0=s0,s1=s1,z=top,outer0=outer(s0),outer1=outer(s1),inner0=sd(s0,tread_d),inner1=sd(s1,tread_d)))
# Front stone envelope follows the visible straight rail, not the narrowing
# upper ink triangle. The actual substrate behind the facing stays unspecified.
rail_band('R04_STONE_SIDE_ENVELOPE',A,E,tread_d,P['front_wall_difference_canonical'],0,0,LOW,UP,stone,'photographed_stone_side_envelope')
# Back wall follows the PDF curve, with separately documented upper extension.
for i in range(64):
 s0=W+(L-W)*i/64;s1=W+(L-W)*(i+1)/64;a=xy(outer(s0));b=xy(outer(s1));n=up.cross((b-a).normalized())*P['back_wall_thickness_m'];poly=[a,b,b-n,a-n]
 mesh(f'R04_RECESS_BACK_{i:02}',[tuple(p+up*z) for z in [0,head] for p in poly],[(3,2,1,0),(4,5,6,7)]+[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)],stone,'curved_stair_recess_back_envelope')
# Local rectangular aperture in the old front plane. Preserve all portions
# outside its s-range and above its head, and retain the old source objects.
def canonical(v):
 M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];o=C['canonical_to_pdf_offset'];a=v.x+293425-M[0][2];b=v.y+5499960-M[1][2];det=M[0][0]*M[1][1]-M[0][1]*M[1][0];u=(M[1][1]*a-M[0][1]*b)/det;w=(-M[1][0]*a+M[0][0]*b)/det;return [(u-o[0])/k,(w-o[1])/k]
for old in list(S.objects):
 if not old.name.startswith('P05_MAIN_ATRIUM_BASE_5') or old.type!='MESH' or old.hide_render:continue
 verts=[old.matrix_world@v.co for v in old.data.vertices];p0,p1=verts[:2];s0=sum(canonical(p0));s1=sum(canonical(p1));lo,hi=sorted([(W-s0)/(s1-s0),(L-s0)/(s1-s0)]);lo=max(0,lo);hi=min(1,hi)
 if hi<=lo:continue
 z0=min(v.z for v in verts);z1=max(v.z for v in verts);old.hide_render=True;old.hide_set(True);old['status']='superseded_R04_stair_recess_opening';replaced.append(old.name)
 for suffix,t0,t1,bot,top in [('BEFORE',0,lo,z0,z1),('AFTER',hi,1,z0,z1),('ABOVE',lo,hi,head,z1)]:
  if t1-t0<1e-7 or top-bot<1e-7:continue
  l=p0.lerp(p1,t0);rr=p0.lerp(p1,t1);l.z=rr.z=0;ob=mesh(old.name+'_R04_'+suffix,[tuple(p+up*z) for p,z in [(l,bot),(rr,bot),(rr,top),(l,top)]],[(0,1,2,3)],stone,'retained_schematic_front_plane');made.remove(ob.name)
# Reveal across the recess, closing to its back curve at each jamb.
for label,s in [('FOOT',W),('TOP',L)]:
 p=outer(s);front=sd(s,P['front_wall_difference_canonical']);eps=.18/scale*math.sqrt(2);jamb_poly=[p,front,sd(s+eps,P['front_wall_difference_canonical']),outer(s+eps)]
 if label=='FOOT':prism('R04_RECESS_JAMB_'+label,jamb_poly,0,head,stone,'recess_jamb_envelope')
 else:
  prism('R04_RECESS_TOP_BELOW_LANDING',jamb_poly,0,UP,stone,'upper_landing_support_envelope')
  prism('R04_RECESS_TOP_LINTEL',jamb_poly,UP+P['upper_landing_exit_height_m'],head,stone,'upper_exit_lintel_candidate')
poly=[outer(W+(L-W)*i/64) for i in range(65)]+[sd(L,P['front_wall_difference_canonical']),sd(W,P['front_wall_difference_canonical'])]
prism('R04_RECESS_HEAD',poly,head,head+.25,stone,'recess_head_envelope')
# Flat connector and inclined guard. Panel count is a candidate; tube/radius
# meets the existing curved return exactly in the calibrated coordinate frame.
dg=lambda width:math.sqrt(2)*width/scale
spans=[(return_s,A)]+[(A+(E-A)*i/P['guard_panels_candidate'],A+(E-A)*(i+1)/P['guard_panels_candidate']) for i in range(P['guard_panels_candidate'])]
for i,(s0,s1) in enumerate(spans):
 gap=dg(Q['panel_joint_gap_m'])/2;z0=height(s0);z1=height(s1)
 rail_band(f'R04_GLASS_{i:02}',s0+gap,s1-gap,guard_d-dg(Q['glass_thickness_m'])/2,guard_d+dg(Q['glass_thickness_m'])/2,height(s0+gap)+.02,height(s1-gap)+.02,height(s0+gap)+GH-.015,height(s1-gap)+GH-.015,glass,'inclined_guard_glass_candidate')
 rail_band(f'R04_GLASS_BASE_{i:02}',s0,s1,guard_d-dg(.038)/2,guard_d+dg(.038)/2,z0,z1,z0+.024,z1+.024,metal,'guard_base_channel_envelope')
for label,s0,s1 in [('FOOT',return_s,A),('SLOPE',A,E)]:tube('R04_HANDRAIL_'+label,at(s0,guard_d,height(s0)+GH),at(s1,guard_d,height(s1)+GH),Q['top_rail_diameter_m'])
# Local upper-floor clearance, never an across-the-building floor deletion.
aperture=[outer(A+(L-A)*i/64) for i in range(65)]+[sd(L,guard_d+1),sd(A,guard_d+1)];cut=prism('R04_UPPER_FLOOR_STAIR_CUTTER',aperture,UP-.6,UP+.2,stone,'hidden_candidate_upper_floor_aperture');cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE';cutters.append(cut.name)
floor=bpy.data.objects['P05_FLOOR_LP1_BRIDGE'];mod=floor.modifiers.new('R04 conditional upper stair approach','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
S['stage']='R04 complete upper stair candidate with unresolved upper-plan interpretation';S['current_file']=out.name;bpy.data.texts.new('R04_STAIR_NOTES').write(json.dumps(P,indent=2))
cd=bpy.data.cameras.new('R04_STAIR_REVIEW');cam=bpy.data.objects.new(cd.name,cd);root.objects.link(cam);target=at((W+L)/2+10,guard_d,3.8);cam.location=target+normal*20-axis*5+up*5;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=18;S.camera=cam
S.render.resolution_x=1600;S.render.resolution_y=1100;S.render.resolution_percentage=100;S.cycles.samples=48;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/R04_upper_stair.png');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
visibility={o.name:o.hide_render for o in S.objects};keep=set(made+['R03_PODIUM_1_REPAIRED','R03_PODIUM_2_REPAIRED','R03_PODIUM_3_WITH_RECESS','P05_FLOOR_L00_GH'])|{o.name for o in S.objects if o.name.startswith('R03_') and not o.hide_render}
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
bpy.ops.render.render(write_still=True)
for name,value in visibility.items():bpy.data.objects[name].hide_render=value
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=[n for n in made if n not in cutters],cutters=cutters,replaced=replaced,modified_floor='P05_FLOOR_LP1_BRIDGE',steps=steps,guard_d=guard_d,tread_d=tread_d,main_risers_candidate=N,main_rise_m=rise,going_m=pitch*scale/math.sqrt(2),upper_level=UP,podium_level=LOW,guard_height=GH,recess_head=head,return_connector_world=list(at(return_s,guard_d,LOW+GH)),full_flight_is_conditional=True,upper_plan_mask_interpretation_verified=False,construction_acceptance=False)
(B/'reports/R04_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R04_SAVED',out)
