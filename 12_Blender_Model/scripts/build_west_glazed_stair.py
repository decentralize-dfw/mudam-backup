"""R14 two-flight glazed west stair candidate from 066/097 and 102/103."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/west_glazed_stair.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};UP=Z['Z_LP1_FINISH'];MID=UP*P['mid_height_fraction'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R14_BATI_CAM_MERDIVEN_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('P09_WEST_GLAZED_STAIR_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];steps=[];panels=[];frames=[];keys=set();stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];floor=bpy.data.materials['P05_FLOOR_REFERENCE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];up=Vector((0,0,1))
frame_metal=metal.copy();frame_metal.name='R14_DARK_COATED_FRAME_CANDIDATE';bsdf=frame_metal.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.025,.03,.035,1);bsdf.inputs['Metallic'].default_value=.25;bsdf.inputs['Roughness'].default_value=.32
def point(u,v,z=0):
 x=(u+v)/2;y=(u-v)/2;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='WEST_GLAZED_STAIR',level_id='L00_LP1',source_ids=','.join(P['source_ids']),confidence_xy='C/D registered source edges',confidence_z='D inherited floor and equal split',confidence_detail='D sizes, second-flight count and modules',parameter_ids='west_glazed_stair.json',status='conditional_two_flight_candidate',assumption_note='066 has 17 visible risers; second-flight count, equal split and camera pose unverified.',export_group='R14_CANDIDATE').items():ob[k]=v
 made.append(name);return ob
def prism(name,poly,z0,z1,mat,kind):
 N=len(poly);return mesh(name,[tuple(p+up*z) for z in [z0,z1] for p in poly],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],mat,kind)
def rect(name,u0,u1,v0,v1,z0,z1,mat,kind):return prism(name,[point(u0,v0),point(u1,v0),point(u1,v1),point(u0,v1)],z0,z1,mat,kind)
def solid(name,ps,n,depth,mat,kind):
 N=len(ps);return mesh(name,[tuple(p) for p in ps]+[tuple(p-n*depth) for p in ps],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],mat,kind)
def tube(name,a,b,diam):
 axis=(b-a).normalized();ref=up if abs(axis.z)<.9 else Vector((1,0,0));x=axis.cross(ref).normalized()*diam/2;y=axis.cross(x).normalized()*diam/2;N=16;ring=[x*math.cos(i*math.tau/N)+y*math.sin(i*math.tau/N) for i in range(N)];ob=mesh(name,[tuple(p+q) for p in [a,b] for q in ring],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],metal,'round_wall_rail_candidate')
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
def frame(a,b,n):
 key=tuple(sorted(tuple(round(v,5) for v in p) for p in [a,b]))
 if key in keys:return
 keys.add(key);side=n.cross((b-a).normalized())*P['frame_width_m']/2;name=f'R14_FRAME_{len(frames):03}';solid(name,[a-side,b-side,b+side,a+side],n,P['frame_depth_m'],frame_metal,'glazed_stair_frame_candidate');frames.append(name)
def pane(ps,n):
 cent=sum(ps,Vector())/4;short=min((a-b).length for a,b in zip(ps,ps[1:]+ps[:1]));fac=max(.85,1-.055/short);name=f'R14_GLASS_{len(panels):03}';solid(name,[cent+(p-cent)*fac for p in ps],n,P['glass_thickness_m'],glass,'flat_glazing_candidate');panels.append(name)
 for a,b in zip(ps,ps[1:]+ps[:1]):frame(a,b,n)
u0,u1=P['first_u'];v0,v1=P['first_v'];s0,s1=P['second_u'];v_end,v_turn=P['second_v'];th=P['slab_display_thickness_m'];head=P['glass_head_clearance_m']
flights=[dict(id='A',a=point(u0,(v0+v1)/2),b=point(u1,(v0+v1)/2),width=(point(u0,v1)-point(u0,v0)).length,z0=0,z1=MID,inner=point(u0,v0),outer=point(u0,v1),count=P['riser_counts_candidate'][0]),dict(id='B',a=point((s0+s1)/2,v_turn),b=point((s0+s1)/2,v_end),width=(point(s1,v_turn)-point(s0,v_turn)).length,z0=MID,z1=UP,inner=point(s0,v_turn),outer=point(s1,v_turn),count=P['riser_counts_candidate'][1])]
paths=[]
for f in flights:
 direction=(f['b']-f['a']).normalized();length=(f['b']-f['a']).length;side=(f['outer']-f['inner']).normalized();N=f['count'];rise=(f['z1']-f['z0'])/N
 for j in range(N):
  a=f['a']+direction*length*j/N;b=f['a']+direction*length*(j+1)/N;poly=[a-side*f['width']/2,b-side*f['width']/2,b+side*f['width']/2,a+side*f['width']/2];za=f['z0']+rise*j-th;zb=f['z0']+rise*(j+1)-th;zt=f['z0']+rise*(j+1);vs=[tuple(p+up*z) for p,z in zip(poly,[za,zb,zb,za])]+[tuple(p+up*zt) for p in poly];name=f'R14_TREAD_{f["id"]}_{j+1:02}';mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone,'stone_tread_with_sloping_slab_envelope');steps.append(dict(name=name,center=list((a+b)/2+up*zt),side=list(side),width=f['width'],z=zt,flight=f['id']))
 # Stone on the inside; no invented glazed guard on that side of 066.
 a=f['inner'];b=a+direction*length;prism('R14_INNER_WALL_'+f['id'],[a,b,b-side*P['wall_display_thickness_m'],a-side*P['wall_display_thickness_m']],0,Z['Z_ROOF_MAIN_BASE'],stone,'stone_inner_boundary_candidate')
 ha=a+side*.08+up*(f['z0']+P['wall_handrail_height_m']);hb=b+side*.08+up*(f['z1']+P['wall_handrail_height_m']);tube('R14_WALL_RAIL_'+f['id'],ha,hb,P['wall_handrail_diameter_m'])
 for j in range(5):
  p=ha.lerp(hb,j/4);tube(f'R14_RAIL_STUB_{f["id"]}_{j}',p-side*.08,p,.018)
 # Outer side and roof follow the two slopes shown in 097.
 a=f['outer'];b=a+direction*length;solid('R14_OUTER_FASCIA_'+f['id'],[a+up*(f['z0']-th),b+up*(f['z1']-th),b+up*(f['z1']+.015),a+up*(f['z0']+.015)],side,.045,frame_metal,'visible_opaque_sloping_edge_band_candidate')
 for j in range(P['flight_glass_bays_candidate']):
  t0=j/P['flight_glass_bays_candidate'];t1=(j+1)/P['flight_glass_bays_candidate'];a=f['outer']+direction*length*t0;b=f['outer']+direction*length*t1;za=f['z0']+(f['z1']-f['z0'])*t0;zb=f['z0']+(f['z1']-f['z0'])*t1;pane([a+up*(za-.05),b+up*(zb-.05),b+up*(zb+head),a+up*(za+head)],side);q=[a+up*(za+head),b+up*(zb+head),b-side*f['width']+up*(zb+head),a-side*f['width']+up*(za+head)];normal=(q[1]-q[0]).cross(q[3]-q[0]).normalized();normal=normal if normal.z>0 else -normal;pane(q,normal)
 paths.append(dict(id=f['id'],a=list(f['a']),b=list(f['b']),width=f['width'],z0=f['z0'],z1=f['z1'],risers=N,rise=rise,going=length/N))
rect('R14_CORNER_LANDING',s0,s1,v0,v1,MID-th,MID,stone,'quarter_turn_flat_landing')
rect('R14_GROUND_ENTRY',P['ground_entry_u'][0],u0,v0,v1,-.2,0,floor,'source_ground_entry_connection')
rect('R14_UPPER_LANDING',s0-4,s1,P['upper_connection_v'],P['upper_landing_v'][1],UP-.2,UP,floor,'source_upper_connection_candidate')
# The source white circulation strip crosses the older unbroken gallery surface.
# Retain the lower wall and the upper head, leaving the upper entry physically open.
oldwall=bpy.data.objects['P05_GALLERY_HALL_WEST3'];oldwall.hide_render=True;oldwall.hide_set(True)
def wall_segment(name,y0,y1,z0,z1):
 x=862.5;a=point(x+y0,x-y0);b=point(x+y1,x-y1);ex=(point(x+y0+1,x-y0+1)-a).normalized();prism(name,[a,b,b-ex*.3,a-ex*.3],z0,z1,stone,'upper_source_circulation_portal_wall')
wall_segment('R14_GALLERY_WALL_RETAINED',356,P['upper_portal_source_y'][0],0,Z['Z_ROOF_MAIN_BASE'])
wall_segment('R14_GALLERY_WALL_BELOW',*P['upper_portal_source_y'],0,UP)
wall_segment('R14_GALLERY_WALL_HEAD',*P['upper_portal_source_y'],UP+head,Z['Z_ROOF_MAIN_BASE'])
# Two exterior faces and roof of the corner, all flat at the intermediate level.
eu=(point(1,0)-point(0,0)).normalized();ev=(point(0,1)-point(0,0)).normalized()
pane([point(s0,v1,MID),point(s1,v1,MID),point(s1,v1,MID+head),point(s0,v1,MID+head)],ev)
pane([point(s1,v0,MID),point(s1,v1,MID),point(s1,v1,MID+head),point(s1,v0,MID+head)],eu)
solid('R14_CORNER_FASCIA_V',[point(s0,v1,MID-th),point(s1,v1,MID-th),point(s1,v1,MID+.015),point(s0,v1,MID+.015)],ev,.045,frame_metal,'corner_opaque_edge_band_candidate')
solid('R14_CORNER_FASCIA_U',[point(s1,v0,MID-th),point(s1,v1,MID-th),point(s1,v1,MID+.015),point(s1,v0,MID+.015)],eu,.045,frame_metal,'corner_opaque_edge_band_candidate')
pane([point(s0,v0,MID+head),point(s1,v0,MID+head),point(s1,v1,MID+head),point(s0,v1,MID+head)],up)
end=P['upper_landing_v'][0];pane([point(s1,end,UP),point(s1,v_end,UP),point(s1,v_end,UP+head),point(s1,end,UP+head)],eu);pane([point(s0,end,UP+head),point(s1,end,UP+head),point(s1,v_end,UP+head),point(s0,v_end,UP+head)],up)
solid('R14_UPPER_FASCIA',[point(s1,end,UP-th),point(s1,v_end,UP-th),point(s1,v_end,UP+.015),point(s1,end,UP+.015)],eu,.045,frame_metal,'upper_opaque_edge_band_candidate')
S['stage']='R14 west glazed stair candidate pending source and circulation checks';S['current_file']=out.name;bpy.data.texts.new('R14_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,panels=panels,frames=frames,steps=steps,flights=paths,mid_z=MID,upper_z=UP,changed_inherited_objects=[oldwall.name],hidden_superseded=[oldwall.name],photo_visible_count=17,full_riser_count_verified=False,construction_acceptance=False);(B/'reports/R14_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R14',len(made),paths)
