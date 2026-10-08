"""Replace unsupported full-height glass at the photographed open GH east portal."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/grand_hall_portal.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R02_GH_GECISI_{version}.blend'
if out.exists():raise RuntimeError('Choose new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('P07_GH_EAST_PORTAL_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);mat=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];made=[]
def xy(p):
 k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+off[0];v=k*p[1]+off[1]
 return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
up=Vector((0,0,1));a,b=map(xy,P['edge_canonical']);axis=(b-a).normalized();normal=up.cross(axis);depth=P['wall_display_depth_m'];jamb=P['jamb_display_width_m'];beam=P['ground_clear_height_m'];head=P['upper_clear_head_m']
def box(name,l,r,z0,z1):
 side=normal*depth/2;poly=[l-side,r-side,r+side,l+side];verts=[tuple(p+up*z) for z in [z0,z1] for p in poly];faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,zone_id='GH_EAST_PORTAL',level_id='MULTI',opening_id=P['opening_id'],element_type='portal_stone_envelope',source_ids=','.join(P['source_ids']),status='conditional_visible_opening',confidence_xy='C plan and revised roof endpoints',confidence_z='D photo proportions',confidence_detail='D unmeasured envelope',parameter_ids='grand_hall_portal.json',assumption_note='Open portal supported by 026/032; dimensions and structural substrate unverified.').items():ob[k]=v
 made.append(name);return ob
for name in P['superseded']:
 old=bpy.data.objects[name];old.hide_render=True;old.hide_set(True);old['status']='superseded_unsupported_full_height_glass'
# Locally clear the photographed corridor from older schematic wall planes.
# Preserve their remaining surfaces and retain the old objects for provenance.
trimmed=[]
for name in P['clearance_trim_targets']:
 old=bpy.data.objects[name];vs=[old.matrix_world@v.co for v in old.data.vertices];p0,p1=vs[:2];z0=min(v.z for v in vs);z1=max(v.z for v in vs);length=(b-a).length
 u0=(p0-a).dot(axis);u1=(p1-a).dot(axis);v0=(p0-a).dot(normal);v1=(p1-a).dot(normal);lo=0.;hi=1.
 for start,end,minimum,maximum in [(u0,u1,-.02,length+.02),(v0,v1,-P['portal_clearance_depth_m']/2,P['portal_clearance_depth_m']/2)]:
  delta=end-start
  if abs(delta)<1e-10:
   if not minimum<=start<=maximum:hi=-1;break
  else:
   t0,t1=sorted([(minimum-start)/delta,(maximum-start)/delta]);lo=max(lo,t0);hi=min(hi,t1)
 if hi<=lo:continue
 old.hide_render=True;old.hide_set(True);old['status']='superseded_locally_trimmed_to_plan_passage';trimmed.append(name)
 def retained_surface(suffix,t0,t1,bot,top):
  if t1-t0<1e-7 or top-bot<1e-7:return
  l=p0.lerp(p1,t0);rr=p0.lerp(p1,t1);l.z=0;rr.z=0;me=bpy.data.meshes.new(name+suffix);me.from_pydata([tuple(v+up*z) for v,z in [(l,bot),(rr,bot),(rr,top),(l,top)]],[],[(0,1,2,3)]);me.update();ob=bpy.data.objects.new(me.name,me);root.objects.link(ob)
  for m in old.data.materials:me.materials.append(m)
  for key in old.keys():ob[key]=old[key]
  ob['element_id']=ob.name;ob['status']='schematic_wall_locally_trimmed';ob['parameter_ids']='grand_hall_portal.json';ob['assumption_note']='Old wall remains schematic. Only its intrusion into the plan/photo-supported passage corridor was removed.'
 retained_surface('_R02_BEFORE',0,lo,z0,z1);retained_surface('_R02_AFTER',hi,1,z0,z1);retained_surface('_R02_ABOVE',lo,hi,head,z1)
box('P07_GH_EAST_PORTAL_JAMB_N',a,a+axis*jamb,0,head)
box('P07_GH_EAST_PORTAL_JAMB_S',b-axis*jamb,b,0,head)
box('P07_GH_EAST_PORTAL_CROSS_BEAM',a+axis*jamb,b-axis*jamb,beam,beam+P['cross_beam_height_m'])
opening=bpy.data.objects.new(P['opening_id'],None);root.objects.link(opening);opening.location=(a+b)/2;opening['element_type']='open_passage_no_glass';opening['source_ids']='021,026,032,102,103';opening['ground_clear_height_m']=beam;opening['upper_clear_head_m']=head
camera_data=bpy.data.cameras.new('P07_GH_PORTAL_REVIEW');cam=bpy.data.objects.new(camera_data.name,camera_data);root.objects.link(cam);cam.location=xy([550,435])+up*2;target=(a+b)/2+up*4.8;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=22;S.camera=cam;S.render.resolution_x=1400;S.render.resolution_y=1600;S.render.resolution_percentage=100;S.render.filepath=str(B/'renders/qa/R02_GH_portal.png');S.cycles.samples=48;S['current_file']=out.name;S['stage']='R02 open GH east portal after 026/032 photo check';bpy.data.texts.new('R02_GH_PORTAL_NOTES').write(json.dumps(P,indent=2))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,hidden_superseded=P['superseded']+trimmed,portal_endpoints=[list(a),list(b)],normal=list(normal),ground_clear=beam,beam_top=beam+P['cross_beam_height_m'],upper_head=head,construction_acceptance=False)
(B/'reports/R02_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R02_SAVED',out)
