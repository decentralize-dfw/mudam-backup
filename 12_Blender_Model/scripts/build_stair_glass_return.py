"""R03: photo-observed upper-stair foot return, editable conditional dimensions."""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
sys.path.insert(0,str(B/'scripts'));from stair_outline import repair_closure
P=json.loads((B/'config/stair_glass_return.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R03_MERDIVEN_CAM_DONUSU_{version}.blend'
if out.exists():raise RuntimeError('Choose new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene
root=bpy.data.collections.new('P15_GH_UP_FOOT_RETURN_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];made=[];cutters=[]
up=Vector((0,0,1));podium_top=json.loads((B/'config/stair_podium.json').read_text())['draft_podium_top_z']
def xy(p):
 k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+off[0];v=k*p[1]+off[1]
 return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
center=xy(P['center_canonical']);axis=(xy([P['center_canonical'][i]+P['flight_direction_canonical'][i] for i in range(2)])-center).normalized()
normal=(xy([P['center_canonical'][0]+1,P['center_canonical'][1]-1])-center).normalized()
def mesh(name,verts,faces,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for key,value in dict(element_id=name,element_type=kind,level_id='L00',zone_id='GH_UP',source_ids=','.join(P['source_ids']),status='conditional_photo_component',confidence_xy='D inside plan-traced podium; no metric photo pose',confidence_z='D photo proportions',confidence_detail='D unmeasured detail',parameter_ids='stair_glass_return.json',assumption_note='Observed component type; numeric dimensions, circle approximation, seams and placement are conditional. Inclined continuation unresolved.',export_group='R03_STAIR_FOOT_STUDY').items():ob[key]=value
 made.append(name);return ob
def swept_profile(name,profile,start,end,mat,kind,segments=96,closed=False):
 # Profile is a closed ring in radial/height coordinates. Sweeping it makes
 # explicit glass / channel / rail solids rather than render-only curves.
 count=segments if closed else segments+1;n=len(profile);verts=[]
 for j in range(count):
  a=start+(end-start)*j/segments;radial=normal*math.cos(a)+axis*math.sin(a)
  verts.extend(tuple(center+radial*r+up*z) for r,z in profile)
 faces=[]
 for j in range(segments):
  jj=(j+1)%count
  for i in range(n):faces.append((j*n+i,jj*n+i,jj*n+(i+1)%n,j*n+(i+1)%n))
 if not closed:faces.extend([tuple(range(n-1,-1,-1)),tuple((count-1)*n+i for i in range(n))])
 return mesh(name,verts,faces,mat,kind)
def band(name,r0,r1,z0,z1,start,end,mat,kind,closed=False):
 return swept_profile(name,[(r0,z0),(r1,z0),(r1,z1),(r0,z1)],start,end,mat,kind,closed=closed)
rad=P['radius_m'];sweep=-math.radians(P['arc_degrees']);z=podium_top;gh=P['rail_height_above_podium_m'];th=P['glass_thickness_m'];ch=P['channel_height_m'];cw=P['channel_width_m'];ct=P['channel_wall_m'];gap=P['panel_joint_gap_m']/rad
panes=[]
for i in range(P['panel_count_candidate']):
 a=sweep*i/P['panel_count_candidate']-gap/2;b=sweep*(i+1)/P['panel_count_candidate']+gap/2
 panes.append(band(f'R03_RETURN_GLASS_{i+1}',rad-th/2,rad+th/2,z+ct,z+gh-P['top_rail_diameter_m']/3,a,b,glass,'curved_return_glass').name)
 # Separate physical sides and bottom preserve the glass socket, no solid
 # metal slab occupying the entire pane thickness above its base.
 band(f'R03_CHANNEL_OUTER_{i+1}',rad+cw/2-ct,rad+cw/2,z,z+ch,a,b,metal,'base_channel_outer_lip')
 band(f'R03_CHANNEL_INNER_{i+1}',rad-cw/2,rad-cw/2+ct,z,z+ch,a,b,metal,'base_channel_inner_lip')
 band(f'R03_CHANNEL_WEB_{i+1}',rad-cw/2,rad+cw/2,z,z+ct,a,b,metal,'base_channel_web')
rr=P['top_rail_diameter_m']/2
profile=[(rad+rr*math.cos(j*math.tau/20),z+gh+rr*math.sin(j*math.tau/20)) for j in range(20)]
swept_profile('R03_RETURN_ROUND_HANDRAIL',profile,0,sweep,metal,'continuous_round_metal_return')
# Recess is a real cut into podium 3. A retained hidden source preserves the
# previous source-traced podium without mutating its source mesh.
podium_config=json.loads((B/'config/stair_podium.json').read_text());closure_repairs=[];repaired_footprints=[]
for index,contour in enumerate(podium_config['contours']):
 old=bpy.data.objects[f'P09_PODIUM_{index+1}'];old.hide_render=True;old.hide_set(True);old['status']='superseded_by_R03_repaired_closure'
 points,repairs=repair_closure(contour['footprint_canonical']);closure_repairs.append(dict(podium=index+1,repairs=repairs));repaired_footprints.append(points)
 poly=[xy(p) for p in points];n=len(poly);lookup={tuple(p):i for i,p in enumerate(poly)}
 def ix(v):return v if isinstance(v,int) else lookup[tuple(v)]
 tris=tessellate_polygon([poly]);faces=[tuple(ix(v) for v in reversed(t)) for t in tris]+[tuple(ix(v)+n for v in t) for t in tris]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 name='R03_PODIUM_3_WITH_RECESS' if index==2 else f'R03_PODIUM_{index+1}_REPAIRED'
 ob=mesh(name,[tuple(p+up*h) for h in [index*podium_config['draft_riser_m'],(index+1)*podium_config['draft_riser_m']] for p in poly],faces,stone,'source_podium_with_repaired_closure')
 ob['parameter_ids']='stair_podium.json;stair_glass_return.json';ob['assumption_note']='Tiny self-crossing at PDF ink-to-wall closure removed at exact line intersection; photographed recess dimensions conditional.'
 if index==2:floor=ob
# A cylinder has no degenerate radial center ring.
def cylinder(name,r,z0,z1,mat,kind):
 n=96;ring=[center+(normal*math.cos(i*math.tau/n)+axis*math.sin(i*math.tau/n))*r for i in range(n)]
 return mesh(name,[tuple(p+up*h) for h in [z0,z1] for p in ring],[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,kind)
recess=P['recess_radius_m'];depth=P['recess_depth_m'];bevel=P['recess_bevel_width_m'];lamp=P['lamp_outer_radius_m'];lens=P['lamp_lens_radius_m']
cut=cylinder('R03_PODIUM_RECESS_CUTTER',recess,z-.10,z+.10,stone,'hidden_editable_recess_cutter');cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE';cutters.append(cut.name)
mod=floor.modifiers.new('Photographed foot-return floor recess candidate','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
swept_profile('R03_RECESSED_STONE_DISH',[(lamp,z-depth),(recess-bevel,z-depth),(recess,z),(recess,z-.10),(lamp,z-.10)],0,math.tau,stone,'recessed_stone_surface_with_lamp_aperture',closed=True)
band('R03_UPLIGHT_DARK_TRIM',lens,lamp,z-depth-.014,z-depth,0,math.tau,metal,'round_uplight_visible_trim',closed=True)
cylinder('R03_UPLIGHT_GLASS_LENS',lens,z-P['lens_depth_below_podium_m']-.008,z-P['lens_depth_below_podium_m'],glass,'recessed_uplight_lens')
# Only visible optical depth is represented. Hidden electrical internals are not.
band('R03_UPLIGHT_VISIBLE_REVEAL',lens-.004,lens,z-.10,z-depth,0,math.tau,metal,'lamp_recess_visible_wall',closed=True)
guide=bpy.data.objects.get('P09_GH_UP_CORRECTED_PATH')
if guide:guide.hide_render=True;guide.hide_set(True);guide['status']='reference_direction_guide_hidden_for_detail_review'
camera_data=bpy.data.cameras.new('R03_RETURN_REVIEW');camera=bpy.data.objects.new(camera_data.name,camera_data);root.objects.link(camera)
camera.location=center-axis*4.1+normal*3.5+up*3.1;target=center+up*.85;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=44;S.camera=camera
S['stage']='R03 photo-supported upper-stair foot return; full flight unresolved';S['current_file']=out.name
S.render.resolution_x=1400;S.render.resolution_y=1300;S.render.resolution_percentage=100;S.render.engine='CYCLES';S.cycles.samples=64;S.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/R03_stair_return.png');bpy.data.texts.new('R03_STAIR_FOOT_NOTES').write(json.dumps(P,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
# Isolated detail view: it must be labeled as such in the review, not passed off
# as an interior photo-matched rendering of the unfinished full stair.
visibility={ob.name:ob.hide_render for ob in S.objects};keep=set(made+['P05_FLOOR_L00_GH'])-set(cutters)
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
bpy.ops.render.render(write_still=True)
for name,value in visibility.items():bpy.data.objects[name].hide_render=value
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=[n for n in made if n not in cutters],cutters=cutters,panes=panes,center_world=list(center),axis_world=list(axis),normal_world=list(normal),podium_top_z=z,recess_z=z-depth,lens_z=z-P['lens_depth_below_podium_m'],radius=rad,arc_degrees=P['arc_degrees'],source_ids=P['source_ids'],podium_closure_repairs=closure_repairs,repaired_footprints_canonical=repaired_footprints,render_is_isolated_component=True,metric_photo_pose_verified=False,full_flight_modeled=False,construction_acceptance=False)
(B/'reports/R03_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R03_SAVED',out)
