"""R08 reading-room funnel and 24-arm light candidate, based on 015/016."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/reading_ceiling.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};UP=Z['Z_LP1_FINISH']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R08_OKUMA_TAVANI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('P17_READING_CEILING_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
def point(p,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
cx,cy=P['center_canonical'];center=point([cx,cy]);up=Vector((0,0,1));ex=(point([cx+1,cy])-center).normalized();ey=(point([cx,cy+1])-center).normalized();outer=[point(p,P['ceiling_lower_z']) for p in P['outer_canonical']];d=P['roof_half_diagonal_canonical'];inner=[point(p,P['ceiling_upper_z']) for p in [[cx,cy-d],[cx+d,cy],[cx,cy+d],[cx-d,cy]]];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];made=[];cutters=[]
lamp=bpy.data.materials.new('R08_LUMINOUS_TUBE_PREVIEW');lamp.use_nodes=True;bs=lamp.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.8,.77,.61,1);bs.inputs['Emission Color'].default_value=(1,.88,.62,1);bs.inputs['Emission Strength'].default_value=4;bs.inputs['Roughness'].default_value=.3
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='READING',level_id='LP1_ROOF',source_ids=','.join(P['source_ids']),confidence_xy='C room plan, D ceiling outline transfer',confidence_z='D candidate below inherited curb height',confidence_detail='C 24 visible arms; D sizes and fixture height',confidence_material='C stone/glass/metal/light families; D uncalibrated',parameter_ids='reading_ceiling.json',status='conditional_reading_ceiling_candidate',assumption_note='015/016 topology and 24 radial light arms. Exact ceiling levels, fixture dimensions, wire network and exterior lantern remain unresolved.',export_group='R08_CANDIDATE',collision_role='review_only').items():ob[k]=v
 made.append(name);return ob
def solid(name,poly,delta,mat,kind):
 n=len(poly);return mesh(name,[tuple(v) for v in poly]+[tuple(v+delta) for v in poly],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,kind)
def tube(name,a,b,diam,mat,kind,sides=16):
 t=(b-a).normalized();ref=up if abs(t.z)<.9 else ex;u=t.cross(ref).normalized()*diam/2;v=t.cross(u).normalized()*diam/2;ring=[u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides) for i in range(sides)];ob=mesh(name,[tuple(p+q) for p in [a,b] for q in ring],[tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)],mat,kind)
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
facets=[]
for i in range(8):
 j=(i+1)%8;k=i//2;poly=[outer[i],outer[j],inner[k]] if i%2==0 else [outer[i],outer[j],inner[(k+1)%4],inner[k]];ob=solid(f'R08_STONE_CEILING_{i}',poly,up*P['ceiling_display_thickness_m'],stone,'inclined_stone_ceiling_finish_envelope');facets.append(ob.name)
# Cut the roof deck along the funnel, not merely a vertical square hole. The
# pre-existing vertical aperture remains independently editable above the funnel.
vertices=outer+inner;faces=[tuple(range(7,-1,-1)),tuple(range(8,12))]
for i in range(8):
 j=(i+1)%8;k=i//2;faces.append((i,j,8+k) if i%2==0 else (i,j,8+(k+1)%4,8+k))
cut=mesh('R08_FUNNEL_VOID',list(map(tuple,vertices)),faces,stone,'hidden_source_limited_funnel_cutter');cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE';cutters.append(cut.name)
for name in ['P05_MAIN_ROOF_DECK','P06_READING_CURB']:
 mod=bpy.data.objects[name].modifiers.new('R08 inclined lightwell opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
# Four clear panes and a cross at the square opening. This is an interior
# candidate; it does not settle the inherited exterior lantern geometry.
top=P['ceiling_upper_z']+.035;origin=center+up*top;corners=[Vector((v.x,v.y,top)) for v in inner];frame=P['skylight_frame_width_m'];depth=P['skylight_frame_depth_m']
for i in range(4):
 a=corners[i];b=corners[(i+1)%4];poly=[origin,a,b];cent=sum(poly,Vector())/3;poly=[cent+(v-cent)*.975 for v in poly];solid(f'R08_SKYLIGHT_GLASS_{i}',poly,up*P['glass_thickness_m'],glass,'square_aperture_glass_candidate');tube(f'R08_SKYLIGHT_EDGE_{i}',a,b,frame,metal,'skylight_perimeter_profile_envelope',4)
for i in range(2):tube(f'R08_SKYLIGHT_CROSS_{i}',corners[i],corners[i+2],frame,metal,'skylight_cross_profile_envelope',4)
fz=P['fixture_z'];ri=P['fixture_inner_radius_m'];ro=P['fixture_outer_radius_m'];tube('R08_LIGHT_CENTRAL_DISK',center+up*(fz-P['fixture_hub_depth_m']/2),center+up*(fz+P['fixture_hub_depth_m']/2),ri*2,metal,'central_light_hub_envelope',64)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ceiling=[bpy.data.objects[n].evaluated_get(deps) for n in facets];anchors=[]
for j in range(P['fixture_arms_observed']):
 a=j*math.tau/P['fixture_arms_observed'];rad=ex*math.cos(a)+ey*math.sin(a);p=center+rad*ri+up*fz;q=center+rad*ro+up*fz;cap=P['fixture_terminal_length_m'];tube(f'R08_LIGHT_TUBE_{j:02}',p+rad*cap,q-rad*cap,P['fixture_tube_diameter_m'],lamp,'radial_luminous_tube');tube(f'R08_LIGHT_INNER_SOCKET_{j:02}',p,p+rad*cap,P['fixture_tube_diameter_m']*1.4,metal,'light_socket_envelope');tube(f'R08_LIGHT_OUTER_SOCKET_{j:02}',q-rad*cap,q,P['fixture_tube_diameter_m']*1.4,metal,'light_socket_envelope')
 raybase=center+rad*3.5+up*UP;hits=[]
 for ob in ceiling:
  inv=ob.matrix_world.inverted();hit,loc,_,_=ob.ray_cast(inv@raybase,inv.to_3x3()@up,distance=15)
  if hit:hits.append(ob.matrix_world@loc)
 assert hits,('No ceiling for wire',j);anchor=min(hits,key=lambda v:v.z);anchor-=up*.03;tube(f'R08_LIGHT_WIRE_{j:02}',q,anchor,P['wire_diameter_m'],metal,'simple_radial_suspension_candidate',8);tube(f'R08_CEILING_ANCHOR_{j:02}',anchor,anchor+up*.03,.016,metal,'ceiling_attachment_envelope',12);anchors.append(dict(index=j,point=list(anchor),tube_end=list(q)))
S['stage']='R08 reading ceiling and 24-arm lighting candidate';S['current_file']=out.name;bpy.data.texts.new('R08_SOURCE_AND_ASSUMPTIONS').write(json.dumps(P,indent=2));cd=bpy.data.cameras.new('R08_READING_UPWARD_REVIEW');cam=bpy.data.objects.new(cd.name,cd);root.objects.link(cam);cam.location=center+up*1.1;cam.rotation_euler=up.to_track_quat('-Z','Y').to_euler();cam.rotation_euler.z+=math.pi/4;cd.lens=28;S.camera=cam;S.render.resolution_x=1500;S.render.resolution_y=1400;S.render.resolution_percentage=100;S.cycles.samples=64;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/R08_reading_upward.png');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
keep=set(made)-set(cutters);keep.update(o.name for o in S.objects if o.name.startswith(('P15_READING_','P17_READING_FLOOR')))
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=[n for n in made if n not in cutters],ceiling_facets=facets,cutters=cutters,roof_boolean_targets=['P05_MAIN_ROOF_DECK','P06_READING_CURB'],floor_z=UP,center_world=list(center),outer_ceiling_world=list(map(list,outer)),inner_ceiling_world=list(map(list,inner)),light_anchors=anchors,fixture_arms_observed=24,fixture_dimensions_verified=False,metric_photo_pose_verified=False,construction_acceptance=False);(B/'reports/R08_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R08_SAVED',out)
