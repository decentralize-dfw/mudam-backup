"""R10: source-registered east spiral and its missing circulation corner."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/east_spiral.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};UP=Z['Z_LP1_FINISH'];H=Z['Z_ROOF_MAIN_BASE'];up=Vector((0,0,1));scale=C['meters_per_canonical_pixel']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R10_DOGU_SPIRAL_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('P09_EAST_SPIRAL_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];floor_mat=bpy.data.materials['P05_FLOOR_REFERENCE'];made=[];cutters=[];changed=[];hidden=[]
def point(p,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
cx,cy=P['center_canonical'];center=point([cx,cy]);ex=(point([cx+1,cy])-center).normalized();ey=(point([cx,cy+1])-center).normalized();RO=P['outer_radius_canonical']*scale;RC=P['core_radius_canonical']*scale;RI=RC+P['inner_tread_clearance_m'];N=P['risers_candidate'];rise=UP/N;E=math.radians(P['top_angle_deg_candidate']);A=E-math.radians(P['turn_degrees_candidate']);DIR=1 if E>A else -1
def polar(a,r,z=0):return center+(ex*math.cos(a)+ey*math.sin(a))*r+up*z
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.get(name)
 if ob is None:ob=bpy.data.objects.new(name,me);root.objects.link(ob)
 else:ob.data=me;changed.append(name)
 me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='EAST_SPIRAL',level_id='L00_LP1',source_ids=','.join(P['source_ids']),confidence_xy='C official102 center and locally registered PDF circle',confidence_z='D inherited floor levels',confidence_detail='D 540-degree/34-riser candidate and detail dimensions',parameter_ids='east_spiral.json',status='conditional_east_spiral_candidate',assumption_note='Distinct 041-044 spiral. Local PDF-to-official translation recorded; no whole-plan warp. Turn, risers and end angle unverified.',export_group='R10_CANDIDATE',collision_role='review_only').items():ob[k]=v
 made.append(name);return ob
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);look={tuple(v):i for i,v in enumerate(poly)}
 def ix(v):return v if isinstance(v,int) else look[tuple(v)]
 tris=tessellate_polygon([poly]);fs=[tuple(ix(v) for v in reversed(t)) for t in tris]+[tuple(ix(v)+n for v in t) for t in tris]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,[tuple(p+up*z) for z in [z0,z1] for p in poly],fs,mat,kind)
def sector(name,a,b,ri,ro,z0,z1,mat,kind,segments=8):
 poly=[polar(a+(b-a)*i/segments,ro) for i in range(segments+1)]+[polar(b-(b-a)*i/segments,ri) for i in range(segments+1)];return prism(name,poly,z0,z1,mat,kind)
def tube(name,a,b,diam,kind,sides=16):
 t=(b-a).normalized();ref=up if abs(t.z)<.9 else ex;u=t.cross(ref).normalized()*diam/2;v=t.cross(u).normalized()*diam/2;ring=[u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides) for i in range(sides)];ob=mesh(name,[tuple(p+q) for p in [a,b] for q in ring],[tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)],metal,kind)
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
def sweep(name,r,profile,a,b,zfunc,mat,kind,segments=96):
 n=len(profile);vs=[]
 for j in range(segments+1):
  t=a+(b-a)*j/segments;vs.extend(tuple(polar(t,r+w,zfunc(t)+z)) for w,z in profile)
 fs=[tuple(range(n-1,-1,-1)),tuple(segments*n+i for i in range(n))]+[(j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n) for j in range(segments) for i in range(n)];return mesh(name,vs,fs,mat,kind)
def round_rail(name,r,a,b,zfunc,slope):
 seg=288 if abs(b-a)>math.tau else 64;sides=20;rad=P['handrail_diameter_m']/2;vs=[]
 for j in range(seg+1):
  t=a+(b-a)*j/seg;axis=(-ex*math.sin(t)*r+ey*math.cos(t)*r+up*slope).normalized();normal=ex*math.cos(t)+ey*math.sin(t);binormal=axis.cross(normal).normalized();p=polar(t,r,zfunc(t));vs.extend(tuple(p+(normal*math.cos(i*math.tau/sides)+binormal*math.sin(i*math.tau/sides))*rad) for i in range(sides))
 fs=[tuple(range(sides-1,-1,-1)),tuple(seg*sides+i for i in range(sides))]+[(j*sides+i,(j+1)*sides+i,(j+1)*sides+(i+1)%sides,j*sides+(i+1)%sides) for j in range(seg) for i in range(sides)];ob=mesh(name,vs,fs,metal,'round_rail_normal_to_path')
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
def hide(ob):ob.hide_render=True;ob.hide_set(True);hidden.append(ob.name);changed.append(ob.name)
# Repair the source-plan open garden floor before placing the staircase.
oldfloor=bpy.data.objects['P05_FLOOR_L00_EAST_GARDEN'];backup=oldfloor.copy();backup.data=oldfloor.data.copy();backup.name='R10_PREVIOUS_GARDEN_FLOOR';root.objects.link(backup);backup.hide_render=True;backup.hide_set(True)
prism(oldfloor.name,list(map(point,P['ground_garden_corrected_outline'])),-.2,0,floor_mat,'official102_garden_floor_including_spiral_corner')
hide(bpy.data.objects['P05_EAST_HIGH']);bpy.data.objects['P05_EAST_HIGH']['status']='superseded_false_wall_across_official102_open_garden'
for ob in list(S.objects):
 if ob.name.startswith('P05_EAST_HIGH_R02_'):
  hide(ob);ob['status']='superseded_false_roof_projection_wall_fragments'
oldwall=bpy.data.objects['P05_GALLERY_HALL_EAST0'];hide(oldwall);verts=[oldwall.matrix_world@v.co for v in oldwall.data.vertices]
for v in verts:v.z=min(v.z,UP)
mesh('R10_GALLERY_GROUND_WALL',list(map(tuple,verts)),[tuple(p.vertices) for p in oldwall.data.polygons],stone,'preserved_ground_wall_surface_below_upper_landing');made.remove('R10_GALLERY_GROUND_WALL')
# Source upper diagonal. Outward thickness leaves the source circulation side open.
a=point([322.5,332.5]);b=point([350.5,360.5]);normal=up.cross((b-a).normalized())
if normal.dot(point([340,340])-a)<0:normal=-normal
prism('R10_UPPER_DIAGONAL_WALL',[a,b,b+normal*.3,a+normal*.3],UP,H,stone,'upper_source_room_boundary_envelope')
steps=[]
for j in range(N-1):
 a=A+(E-A)*j/(N-1);b=A+(E-A)*(j+1)/(N-1);z=(j+1)*rise;name=f'R10_TREAD_{j+1:02}';sector(name,a,b,RI,RO,z-P['tread_display_thickness_m'],z,stone,'radial_step_with_stepped_underside');steps.append(dict(name=name,a=a,b=b,top=z,bottom=z-P['tread_display_thickness_m']))
# Separate cap joint follows 043; hidden structural composition remains unknown.
for name,z0,z1 in [('BODY',0,UP+P['core_top_above_upper_m']-.16),('CAP',UP+P['core_top_above_upper_m']-.16,UP+P['core_top_above_upper_m'])]:
 ob=prism('R10_CORE_'+name,[polar(i*math.tau/128,RC) for i in range(128)],z0,z1,stone,'cylindrical_stone_core_finish_envelope')
 for f in ob.data.polygons:
  if abs(f.normal.z)<.5:f.use_smooth=True
height=P['guard_height_m'];zpath=lambda a:UP*(a-A)/(E-A);th=P['glass_thickness_m'];w=P['stone_edge_band_width_m']
sweep('R10_STONE_OUTER_EDGE',RO,[(-w/2,-P['stone_edge_band_depth_m']),(w/2,-P['stone_edge_band_depth_m']),(w/2,.02),(-w/2,.02)],A,E,zpath,stone,'helical_stone_edge_envelope',256)
for j in range(P['glass_panels_candidate']):
 a=A+(E-A)*j/P['glass_panels_candidate'];b=A+(E-A)*(j+1)/P['glass_panels_candidate'];gap=.002/RO;sweep(f'R10_OUTER_GLASS_{j:02}',RO,[(-th/2,.04),(th/2,.04),(th/2,height-.015),(-th/2,height-.015)],a+DIR*gap,b-DIR*gap,zpath,glass,'curved_glass_panel_candidate',20);sweep(f'R10_GLASS_BASE_{j:02}',RO,[(-.02,.02),(.02,.02),(.02,.045),(-.02,.045)],a,b,zpath,metal,'glass_base_channel_candidate',20)
innerrail=RC+P['core_inner_handrail_offset_m'];round_rail('R10_OUTER_ROUND_RAIL',RO,A,E,lambda a:zpath(a)+height,UP/(E-A));round_rail('R10_INNER_ROUND_RAIL',innerrail,A,E,lambda a:zpath(a)+height,UP/(E-A))
for j in range(13):
 a=A+(E-A)*j/12;z=zpath(a)+height;rad=ex*math.cos(a)+ey*math.sin(a);tube(f'R10_INNER_RAIL_STANDOFF_{j:02}',polar(a,RC,z),polar(a,innerrail-.021,z),.018,'round_rail_standoff_candidate',12);tube(f'R10_INNER_RAIL_PLATE_{j:02}',polar(a,RC-.001,z),polar(a,RC+.008,z),.065,'round_wall_plate_candidate',24)
round_rail('R10_INNER_TOP_RETURN',innerrail,E,E+DIR*math.pi/3,lambda a:UP+height,0)
# Quarter landing, plus the source white circulation triangle. The circular
# void remains open under it, avoiding a solid floor through the helical flight.
corr=prism('R10_UPPER_CIRCULATION_UNION',list(map(point,P['upper_landing_outline_canonical'])),UP-.2,UP,floor_mat,'hidden_source_upper_circulation_union')
cut=prism('R10_UPPER_SPIRAL_VOID',[polar(i*math.tau/128,RO) for i in range(128)],UP-1,UP+1,stone,'hidden_spiral_floor_void')
landing=sector('R10_UPPER_QUARTER_LANDING',E,E+DIR*math.pi/2,RI,RO+.012,UP-.2,UP,stone,'hidden_quarter_landing_union',48)
for ob in [corr,cut,landing]:ob.hide_render=True;ob.hide_set(True);ob.display_type='WIRE';cutters.append(ob.name)
mod=corr.modifiers.new('Spiral clear opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;mod=corr.modifiers.new('Quarter landing','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=landing
upper=bpy.data.objects['P05_FLOOR_LP1_E0'];mod=upper.modifiers.new('R10 source spiral circulation','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=corr;changed.append(upper.name)
# Co-planar Boolean landing seams can leave micron-scale duplicate vertices.
# Keep the editable operands; weld only below 0.01 mm, far below source precision.
mod=upper.modifiers.new('R10 numerical seam weld','WELD');mod.merge_threshold=.00001
end=E+DIR*math.radians(P['upper_landing_outer_guard_end_deg']);sweep('R10_TOP_GLASS_RETURN',RO,[(-th/2,.04),(th/2,.04),(th/2,height-.015),(-th/2,height-.015)],E,end,lambda a:UP,glass,'short_upper_landing_guard_candidate',24);round_rail('R10_OUTER_TOP_RETURN',RO,E,end,lambda a:UP+height,0)
S['stage']='R10 east spiral candidate and source circulation correction';S['current_file']=out.name;bpy.data.texts.new('R10_SOURCE_AND_ASSUMPTIONS').write(json.dumps(P,indent=2));cd=bpy.data.cameras.new('R10_SPIRAL_REVIEW');cam=bpy.data.objects.new(cd.name,cd);root.objects.link(cam);cam.location=center+ex*6-ey*5+up*2;target=center+up*2.6;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=32;S.camera=cam;S.render.resolution_x=1300;S.render.resolution_y=1600;S.render.resolution_percentage=100;S.cycles.samples=64;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/R10_east_spiral.png');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
keep=(set(made)|{upper.name})-set(cutters)
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=sorted(set(made)-set(cutters)),surface_objects=['R10_GALLERY_GROUND_WALL'],changed_inherited_objects=sorted(set(changed)),hidden_superseded=hidden,cutters=cutters,changed_upper_floor=upper.name,changed_ground_floor=oldfloor.name,center_world=list(center),canonical_x_world=list(ex),canonical_y_world=list(ey),outer_radius=RO,inner_radius=RI,core_radius=RC,steps=steps,upper_z=UP,bottom_angle=A,top_angle=E,risers_candidate=N,turn_degrees_candidate=P['turn_degrees_candidate'],rise_m=rise,direction_sign=DIR,real_riser_count_verified=False,construction_acceptance=False);(B/'reports/R10_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R10_SAVED',out)
