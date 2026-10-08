"""R05: downward half-turn stair with observed stepped underside and dual glass rails."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/lower_stair.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']}
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R05_ALT_MERDIVEN_{version}.blend'
if out.exists():raise RuntimeError('Choose new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('P09_GH_DOWN_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];made=[];cutters=[];up=Vector((0,0,1));LOW=Z['Z_LM1_FINISH'];scale=C['meters_per_canonical_pixel'];RO=P['outer_radius_canonical']*scale;RI=P['inner_radius_canonical']*scale;N=P['risers_candidate'];rise=-LOW/N;A=math.radians(P['bottom_angle_deg']);nominal_E=math.pi/4
def xy(p):
 k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+off[0];v=k*p[1]+off[1]
 return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
center=xy(P['center_canonical']);cx,cy=P['center_canonical'];ex=(xy([cx+1,cy])-center).normalized();ey=(xy([cx,cy+1])-center).normalized()
def polar(a,r,z=0):return center+(ex*math.cos(a)+ey*math.sin(a))*r+up*z
chord_d=sum(p[0]-p[1] for p in P['opening_chord_canonical'])/2;center_d=cx-cy
def top_angle(r):return math.acos((chord_d-center_d)*scale/(r*math.sqrt(2)))-math.pi/4
def angle(t,r):return A+(top_angle(r)-A)*t
def zrail(a,r):return LOW+(a-A)/(top_angle(r)-A)*(-LOW)
E=top_angle((RI+RO)/2);da=(E-A)/(N-1)
def mesh(name,verts,faces,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='GH_DOWN',level_id='L00_LM1',source_ids=','.join(P['source_ids']),source_date='see manifest',permanent_or_temporary='candidate_permanent',confidence_xy='C fitted PDF visitor geometry',confidence_z='D conditional section level',confidence_detail='D unmeasured candidate',confidence_material='D generic surface family',parameter_ids='lower_stair.json',assumption_note='34 risers and detail dimensions are conditional. Stepped underside observed in 052. This is the down stair, not GH_UP.',status='conditional_down_stair',visibility_group='GH_DOWN',export_group='R05_CANDIDATE',collision_role='review_only').items():ob[k]=v
 made.append(name);return ob
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);look={tuple(v):i for i,v in enumerate(poly)}
 def idx(v):return v if isinstance(v,int) else look[tuple(v)]
 tris=tessellate_polygon([poly]);faces=[tuple(idx(v) for v in reversed(t)) for t in tris]+[tuple(idx(v)+n for v in t) for t in tris]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,[tuple(v+up*z) for z in [z0,z1] for v in poly],faces,mat,kind)
def sector(name,t0,t1,r0,r1,z0,z1,mat,kind):
 segments=1 if kind=='visible_nosing_strip_candidate' else 8
 poly=[polar(angle(t0+(t1-t0)*i/segments,r1),r1) for i in range(segments+1)]+[polar(angle(t1-(t1-t0)*i/segments,r0),r0) for i in range(segments+1)];return prism(name,poly,z0,z1,mat,kind)
steps=[]
for j in range(N-1):
 a=j/(N-1);b=(j+1)/(N-1);z=LOW+(j+1)*rise;name=f'R05_TREAD_{j+1:02}';sector(name,a,b,RI,RO,z-P['tread_display_thickness_m'],z,stone,'radial_tread_with_stepped_underside');steps.append(dict(name=name,t0=a,t1=b,a_inner=angle(a,RI),b_inner=angle(b,RI),a_outer=angle(a,RO),b_outer=angle(b,RO),top=z,bottom=z-P['tread_display_thickness_m']))
 # A narrow source-visible nosing strip is only a surface-family placeholder.
 width=P['nosing_band_width_m']/((RI+RO)/2*(E-A));sector(f'R05_NOSING_{j+1:02}',a+.0001,a+width,RI+.03,RO-.03,z-.003,z+.001,metal,'visible_nosing_strip_candidate')
# Sweep a closed section around the helical path. Radial edges remain vertical,
# matching the cylindrical bent-glass interpretation rather than flat chords.
def helix(name,r,profile,a,b,mat,kind,segments=64):
 n=len(profile);verts=[]
 for j in range(segments+1):
  t=a+(b-a)*j/segments;verts.extend(tuple(polar(t,r+dr,zrail(t,r)+dz)) for dr,dz in profile)
 faces=[tuple(range(n-1,-1,-1)),tuple(segments*n+i for i in range(n))]
 faces.extend((j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n) for j in range(segments) for i in range(n))
 return mesh(name,verts,faces,mat,kind)
def round_helix(name,r,rail_height,diameter):
 segments=160;sides=20;end=top_angle(r);verts=[];slope=(-LOW)/(end-A)
 for j in range(segments+1):
  a=A+(end-A)*j/segments;radial=ex*math.cos(a)+ey*math.sin(a);tangent=(-ex*math.sin(a)*r+ey*math.cos(a)*r+up*slope).normalized();binormal=tangent.cross(radial).normalized();p=polar(a,r,zrail(a,r)+rail_height)
  verts.extend(tuple(p+(radial*math.cos(i*math.tau/sides)+binormal*math.sin(i*math.tau/sides))*diameter/2) for i in range(sides))
 faces=[tuple(range(sides-1,-1,-1)),tuple(segments*sides+i for i in range(sides))]+[(j*sides+i,(j+1)*sides+i,(j+1)*sides+(i+1)%sides,j*sides+(i+1)%sides) for j in range(segments) for i in range(sides)]
 ob=mesh(name,verts,faces,metal,'continuous_helical_round_handrail')
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
for side,r in [('INNER',RI),('OUTER',RO)]:
 E_side=top_angle(r)
 w=P['stone_edge_band_width_m'];h=P['railing_height_m'];th=P['glass_thickness_m'];cw=P['base_channel_width_m'];ch=P['base_channel_height_m'];rr=P['rail_diameter_m']/2
 helix(f'R05_STONE_EDGE_{side}',r,[(-w/2,-P['stone_edge_band_depth_m']),(w/2,-P['stone_edge_band_depth_m']),(w/2,.035),(-w/2,.035)],A,E_side,stone,'helical_stone_edge_finish_envelope',128)
 round_helix(f'R05_ROUND_RAIL_{side}',r,h,P['rail_diameter_m'])
 for j in range(P['glass_panels_per_side_candidate']):
  a=A+(E_side-A)*j/P['glass_panels_per_side_candidate'];b=A+(E_side-A)*(j+1)/P['glass_panels_per_side_candidate'];gap=P['glass_joint_gap_m']/r/2
  helix(f'R05_GLASS_{side}_{j:02}',r,[(-th/2,.05),(th/2,.05),(th/2,h-.012),(-th/2,h-.012)],a+gap,b-gap,glass,'curved_helical_glass_pane',16)
  helix(f'R05_BASE_{side}_{j:02}',r,[(-cw/2,.028),(cw/2,.028),(cw/2,.028+ch),(-cw/2,.028+ch)],a,b,metal,'base_channel_envelope',16)
# The broad triangular corner void wraps a retained central floor peninsula.
# 102 supplies the corner, PDF218 the inner curve, 114/055 the topology.
# Extend exterior edges 0.5 canonical pixel outside the existing floor to avoid
# a coplanar Boolean sliver at the old coarse footprint boundary.
left=xy(P['corner_void_canonical'][0]);right=xy(P['corner_void_canonical'][2]);inner_top=polar(top_angle(RI),RI);outer_top=polar(top_angle(RO),RO)
peninsula=[xy(p) for p in P['peninsula_edge_canonical']]
opening=[xy([586.5,333.5]),xy([688.5,333.5]),xy([688.5,435.5]),outer_top,inner_top]+list(reversed(peninsula))
cut=prism('R05_SOURCE_GROUND_OPENING',opening,-.8,.5,stone,'hidden_corner_void_102_with_PDF218_retained_peninsula');cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE';cutters.append(cut.name)
floor=bpy.data.objects['P05_FLOOR_L00_GH'];floor.modifiers['GH_down_void'].object=cut;bpy.data.objects['P05_GH_DOWN_VOID']['status']='superseded_schematic_cut'
old=bpy.data.objects['P05_PATH_GH_DOWN'];old.hide_render=True;old.hide_set(True);old['status']='superseded_by_R05_downward_stair_candidate'
# Offset the guard onto its supporting floor, then sweep separate panes around
# the curved edge. The tiny offset is a provisional mounting allowance.
guard_paths=[[left]+peninsula+[inner_top],[outer_top,right]]
ground_bases=[];ground_support=[]
def path_sweep(name,points,profile,mat,kind):
 verts=[];n=len(profile)
 for j,p in enumerate(points):
  tangent=(points[min(j+1,len(points)-1)]-points[max(0,j-1)]).normalized();normal=up.cross(tangent)
  verts.extend(tuple(p+normal*w+up*z) for w,z in profile)
 faces=[tuple(range(n-1,-1,-1)),tuple((len(points)-1)*n+i for i in range(n))]+[(j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n) for j in range(len(points)-1) for i in range(n)]
 return mesh(name,verts,faces,mat,kind)
h=P['railing_height_m'];th=P['glass_thickness_m'];rr=P['rail_diameter_m']/2
# Split at source curve transitions and at the stair access; keep the access open.
segments=[[left,peninsula[0]],peninsula,[peninsula[-1],inner_top],[outer_top,right]]
index=0
for si,segment in enumerate(segments):
 # Each arc pane follows the sampled Bezier. Straight wings are split into
 # candidate ~1.3 m bays; exact glazing shop drawings are unavailable.
 length=sum((b-a).length for a,b in zip(segment,segment[1:]));bays=max(1,round(length/1.3))
 if len(segment)==2:segment=[segment[0].lerp(segment[-1],j/(bays*8)) for j in range(bays*8+1)]
 # Mounting offset toward retained floor. The source edge is traversed with
 # the floor on its right in world coordinates for the peninsula and wings.
 shifted=[]
 for j,p in enumerate(segment):
  tangent=(segment[min(j+1,len(segment)-1)]-segment[max(j-1,0)]).normalized();shifted.append(p-up.cross(tangent)*.045)
 for b in range(bays):
  lo=round(b*(len(shifted)-1)/bays);hi=round((b+1)*(len(shifted)-1)/bays);pts=shifted[lo:hi+1]
  if len(pts)<2:continue
  # Actual 4 mm pane joint, separate from the continuous base channel.
  glasspts=pts.copy();glasspts[0]=glasspts[0]+(glasspts[1]-glasspts[0]).normalized()*.002;glasspts[-1]=glasspts[-1]-(glasspts[-1]-glasspts[-2]).normalized()*.002
  path_sweep(f'R05_GROUND_EDGE_GLASS_{index}',glasspts,[(-th/2,.03),(th/2,.03),(th/2,h),(-th/2,h)],glass,'ground_peninsula_curved_or_straight_glass_candidate')
  name=f'R05_GROUND_EDGE_BASE_{index}';path_sweep(name,pts,[(-.017,0),(.017,0),(.017,.03),(-.017,.03)],metal,'ground_peninsula_base_channel_candidate');ground_bases.append(name);ground_support.append(list(pts[len(pts)//2]));index+=1
 path_sweep(f'R05_GROUND_EDGE_TOP_RAIL_{si}',shifted,[(rr*math.cos(i*math.tau/20),h+rr*math.sin(i*math.tau/20)) for i in range(20)],metal,'ground_peninsula_round_handrail_candidate')
S['stage']='R05 lower stair candidate with source opening and stepped underside';S['current_file']=out.name;bpy.data.texts.new('R05_DOWN_STAIR_NOTES').write(json.dumps(P,indent=2))
cd=bpy.data.cameras.new('R05_LOWER_REVIEW');cam=bpy.data.objects.new(cd.name,cd);root.objects.link(cam);target=center+up*(LOW*.45);cam.location=center-ex*8+ey*7+up*(LOW+3.5);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=13.5;S.camera=cam
S.render.resolution_x=1500;S.render.resolution_y=1400;S.render.resolution_percentage=100;S.cycles.samples=48;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/R05_lower_stair.png');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
visibility={o.name:o.hide_render for o in S.objects};keep=set(made+['P05_ZONE_LM1_GALLERIES_FOYER'])-set(cutters)
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
# The ground-level straight guard is shown separately with its supporting floor.
for ob in S.objects:
 if ob.name.startswith('R05_GROUND_EDGE'):ob.hide_render=True
bpy.ops.render.render(write_still=True)
for name,value in visibility.items():bpy.data.objects[name].hide_render=value
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=[n for n in made if n not in cutters],cutters=cutters,changed_floor='P05_FLOOR_L00_GH',steps=steps,center_world=list(center),canonical_x_world=list(ex),canonical_y_world=list(ey),outer_radius=RO,inner_radius=RI,lower_z=LOW,risers_candidate=N,rise_m=rise,going_at_midradius_m=(RI+RO)/2*da,top_angle_inner=top_angle(RI),top_angle_outer=top_angle(RO),top_angle_midradius=E,bottom_angle=A,opening_chord_difference_canonical=chord_d,source_opening_path=217,stepped_underside=True,ground_edge_guard_is_conditional=True,ground_guard_bases=ground_bases,ground_guard_support_points=ground_support,ground_void_world=[list(p) for p in opening],ground_peninsula_world=[list(p) for p in peninsula],metric_photo_pose_verified=False,construction_acceptance=False)
(B/'reports/R05_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R05_SAVED',out)
