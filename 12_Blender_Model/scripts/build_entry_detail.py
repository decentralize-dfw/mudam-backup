"""P12 entry pilot: visible flat leaves and separate hardware, mechanism unresolved."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/entry_door_detail.json').read_text());E=json.loads((B/'config/entry_package.json').read_text())['entry'];C=json.loads((B/'config/foundation.json').read_text())['calibration']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_P12_GIRIS_DETAY_{version}.blend'
if out.exists():raise RuntimeError('Choose new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene
root=bpy.data.collections.new('P12_ENTRY_DETAIL_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];made=[];hidden=[];leaves=[]
def xy(p):
 k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+off[0];v=k*p[1]+off[1];return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
a,b=map(xy,E['chain'][3:5]);axis=(b-a).normalized();outward=(xy([575,816])-xy([575,688])).normalized();up=Vector((0,0,1));mid=(a+b)/2;w=E['vestibule_width_m'];depth=E['vestibule_depth_m'];height=P['vestibule_roof_z_m'];front=mid+outward*depth
# 008/013 show the vestibule roof near the main lower transom, not at 2.75 m.
for ob in list(S.objects):
 if ob.name.startswith('P08_VESTIBULE_GLASS_'):
  for vertex in ob.data.vertices:vertex.co.z*=height/E['vestibule_height_m']
 elif ob.name=='P08_VESTIBULE_TOP_GLASS':
  for vertex in ob.data.vertices:vertex.co.z+=height-E['vestibule_height_m']
 elif ob.name.startswith('P08_VESTIBULE_TOP_'):
  for vertex in ob.data.vertices:vertex.co.z+=P['leaf_header_z_m']-E['vestibule_height_m']
 elif ob.name=='P08_VESTIBULE_FRONT_HEAD':
  ob.hide_render=True;ob.hide_set(True);ob['status']='superseded_by_P12_header';hidden.append(ob.name)
 elif ob.name=='ENT-02-L00_GLASS_OVER_DOOR':
  for vertex in ob.data.vertices:
   if vertex.co.z<E['vestibule_height_m']+.01:vertex.co.z=P['leaf_header_z_m']
def mesh(name,verts,faces,material,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(material)
 for key,value in dict(element_id=name,element_type=kind,zone_id='ENT',level_id='L00',opening_id=P['opening_id'],source_ids=','.join(P['source_ids']),status='conditional_visible_detail',confidence_xy='C registered entry; D hardware',confidence_z='D photo proportions',confidence_detail='D unmeasured; mechanism U',parameter_ids='entry_door_detail.json',assumption_note='Flat operable leaf candidate. Pivot mechanism and dimensions unverified; revolving label withdrawn.',export_group='P12_ENTRY_CONDITIONAL').items():ob[key]=value
 made.append(name);return ob
def box(name,a,b,z0,z1,thickness,material,kind):
 side=up.cross((b-a).normalized())*thickness/2;poly=[a-side,b-side,b+side,a+side];verts=[tuple(p+up*z) for z in [z0,z1] for p in poly];faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)];return mesh(name,verts,faces,material,kind)
def tube(name,a,b,d,kind):
 n=12;direction=(b-a).normalized();ref=up if abs(direction.z)<.9 else axis;u=direction.cross(ref).normalized()*d/2;v=direction.cross(u).normalized()*d/2;ring=[u*math.cos(i*2*math.pi/n)+v*math.sin(i*2*math.pi/n) for i in range(n)];vs=[tuple(p+r) for p in [a,b] for r in ring];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,vs,fs,metal,kind)
for ob in list(S.objects):
 if ob.name.startswith('P08_VESTIBULE_POST_'):
  ob.hide_render=True;ob.hide_set(True);ob['status']='superseded_by_P12_round_post_candidate';hidden.append(ob.name)
for side in [-1,1]:
 for end,center in [('BACK',mid+axis*w/2*side),('FRONT',front+axis*w/2*side)]:
  key=f'{side}_{end}';tube('P12_CORNER_POST_'+key,center,center+up*(height+.04),P['corner_post_diameter_m'],'round_corner_post')
  for j,z in enumerate([.12,1.1,height-.08]):tube(f'P12_GLASS_FIXING_{key}_{j}',center+up*z-outward*.04,center+up*z+outward*.04,P['fixing_diameter_m'],'visible_point_fixing_candidate')
# Keep each leaf, its edge profiles and pull handle in one pivot family.
leafwidth=(w-.10-P['leaf_center_gap_m'])/2;z0=P['leaf_foot_clearance_m'];z1=P['leaf_header_z_m']-P['leaf_head_clearance_m']
for row in P['leaf_rows']:
 row_id=row['id']
 for side,angle in zip([-1,1],row['pose_degrees']):
  pivot=mid+outward*row['distance_from_facade_m']+axis*(w/2-.05)*side;empty=bpy.data.objects.new('P12_LEAF_PIVOT_'+row['id']+'_'+str(side),None);root.objects.link(empty);empty.location=pivot;empty.empty_display_size=.12;empty['mechanism_verified']=False;empty['review_angle_degrees']=angle;empty['opening_id']=P['opening_id'];bpy.context.view_layer.update();before=set(made)
  u=-axis*side;q=pivot+u*leafwidth;fw=P['leaf_edge_profile_m'];normal=up.cross(u).normalized()
  box(f'P12_LEAF_{row_id}_{side}_GLASS',pivot+u*.004,q-u*.004,z0+fw,z1-fw,P['leaf_glass_thickness_m'],glass,'door_leaf_glass')
  for label,l,r,bot,top in [('BOTTOM',pivot,q,z0,z0+fw),('TOP',pivot,q,z1-fw,z1)]:box(f'P12_LEAF_{row_id}_{side}_{label}',l,r,bot,top,.045,metal,'door_leaf_edge_profile')
  hand=q-u*.09;lo,hi=row['handle_z_range_m'];offset=outward*P['handle_standoff_m']
  for surface in [-1,1]:
   tube(f'P12_LEAF_{row_id}_{side}_HANDLE_{surface}',hand+up*lo+offset*surface,hand+up*hi+offset*surface,P['handle_diameter_m'],'vertical_pull_handle')
   for j,z in enumerate([lo+.08,hi-.08]):tube(f'P12_LEAF_{row_id}_{side}_HANDLE_FIX_{surface}_{j}',hand+up*z,hand+up*z+offset*surface,.014,'handle_standoff')
  members=sorted(set(made)-before)
  for name in members:
   ob=bpy.data.objects[name];world=ob.matrix_world.copy();ob.parent=empty;ob.matrix_world=world
  empty.rotation_euler.z=math.radians(angle)*side;leaves.append(dict(row=row['id'],pivot=empty.name,objects=members,angle_deg=angle,width_m=leafwidth,height_m=z1-z0))
# Keep top fittings simple and separate until the actual operating mechanism is resolved.
box('P12_FRONT_HEADER',front-axis*w/2,front+axis*w/2,P['leaf_header_z_m']-.10,P['leaf_header_z_m']-.025,.095,metal,'header_envelope_not_mechanism')
S['stage']='P12 entry detail pilot; flat leaf mechanism remains unverified';S['current_file']=out.name;S.camera=bpy.data.objects['P07_ENTRY_DETAIL'];S.render.resolution_x=1600;S.render.resolution_y=1400;S.render.resolution_percentage=100
txt=bpy.data.texts.new('P12_READ_ME');txt.write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True;preferences=bpy.context.preferences.addons['cycles'].preferences;preferences.compute_device_type='OPTIX';preferences.get_devices()
for d in preferences.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/P12_entry_detail.png');bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),leaf_rows=P['leaf_rows'],closed_objects=made,hidden_superseded=hidden,leaf_families=leaves,opening_id=P['opening_id'],mechanism_verified=False,revolving_classification_withdrawn=True,construction_acceptance=False)
(B/'reports/P12_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('P12_SAVED',out)
