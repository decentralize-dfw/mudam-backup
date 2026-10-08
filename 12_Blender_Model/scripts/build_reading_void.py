"""P17 regional reading-floor void and P15 glass-guard pilot; no ceiling invention."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
P=json.loads((B/'config/reading_void.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};UP=Z['Z_LP1_FINISH']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_P17_OKUMA_BOSLUGU_{version}.blend'
if out.exists():raise RuntimeError('Choose a new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene
root=bpy.data.collections.new('P17_READING_VOID_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];floor_mat=bpy.data.materials['P05_FLOOR_REFERENCE'];made=[];cutters=[];replaced=[]
def xy(p):
 k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+off[0];v=k*p[1]+off[1]
 return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
up=Vector((0,0,1));center=xy(P['center_canonical'])
def mesh(name,verts,faces,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='LP1',zone_id='READING',source_ids=','.join(P['source_ids']),status='conditional_regional_pilot',confidence_xy='C visitor plan trace',confidence_z='D section proportions',confidence_detail='D unmeasured dimensions',parameter_ids='reading_void.json',assumption_note='Upper-floor void and roof aperture are distinct. See reading_void.json limitations.',export_group='P17_READING_PILOT').items():ob[k]=v
 made.append(name);return ob
def prism(name,points,z0,z1,mat,kind):
 n=len(points);return mesh(name,[tuple(p+up*z) for z in [z0,z1] for p in points],[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,kind)
def wall(name,a,b,z0,z1,d,mat,kind):
 normal=up.cross((b-a).normalized())*d/2;return prism(name,[a-normal,b-normal,b+normal,a+normal],z0,z1,mat,kind)
def tube(name,a,b,d):
 n=16;direction=(b-a).normalized();u=direction.cross(up).normalized()*d/2;v=direction.cross(u).normalized()*d/2;ring=[u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n) for i in range(n)]
 return mesh(name,[tuple(p+r) for p in [a,b] for r in ring],[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],metal,'round_top_rail')
def diamond(half):
 cx,cy=P['center_canonical'];return [xy(p) for p in [(cx,cy-half),(cx+half,cy),(cx,cy+half),(cx-half,cy)]]
def difference(ob,cut,name):
 mod=ob.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
def cutter(name,poly,z0,z1):
 ob=prism(name,poly,z0,z1,floor_mat,'editable_void_cutter');ob.hide_render=True;ob.hide_set(True);ob.display_type='WIRE';cutters.append(name);return ob
floor=prism('P17_READING_FLOOR',list(map(xy,P['floor_outline_canonical'])),UP-P['floor_display_thickness_m'],UP,floor_mat,'upper_reading_floor')
void=diamond(P['floor_void_half_diagonal_canonical']);cut=cutter('P17_LP1_DIAMOND_VOID',void,UP-1,UP+1);difference(floor,cut,'Upper floor void from 103')
# The old roof deck and curb were opaque across the lantern axis.
roofvoid=diamond(P['roof_aperture_half_diagonal_canonical']);cut=cutter('P17_ROOF_APERTURE_CANDIDATE',roofvoid,UP+1,20)
targets=['P05_MAIN_ROOF_DECK','P06_READING_CURB']
for name in targets:difference(bpy.data.objects[name],cut,'Independent roof aperture candidate')
# Glass guards follow the floor opening, not the room's octagonal wall.
offset=P['railing_offset_from_void_m'];height=P['railing_height_m'];gap=P['railing_glass_gap_m']
for i,(a,b) in enumerate(zip(void,void[1:]+void[:1])):
 a=a+(a-center).normalized()*offset*math.sqrt(2);b=b+(b-center).normalized()*offset*math.sqrt(2);axis=(b-a).normalized()
 wall(f'P15_READING_BASE_{i}',a,b,UP,UP+P['bottom_channel_height_m'],P['bottom_channel_width_m'],metal,'concealed_base_channel_candidate')
 # Butt-ended rail and pane joints remain detailed later; no invented custom corner hub.
 tube(f'P15_READING_RAIL_{i}',a+up*(UP+height),b+up*(UP+height),P['top_rail_diameter_m'])
 for j in range(P['railing_panels_per_side']):
  l=a.lerp(b,j/P['railing_panels_per_side'])+axis*gap/2;r=a.lerp(b,(j+1)/P['railing_panels_per_side'])-axis*gap/2
  wall(f'P15_READING_GLASS_{i}_{j}',l,r,UP+.03,UP+height-.018,P['railing_glass_thickness_m'],glass,'balustrade_glass_candidate')
# Transparent solids replace the old opaque display skin only; keep its unresolved topology.
for old in list(S.objects):
 if old.name.startswith(('P06_READING_SLOPE_','P06_READING_LANTERN_','P06_READING_CAP_')):
  ob=old.copy();ob.data=old.data.copy();ob.name=old.name.replace('P06_','P17_');root.objects.link(ob);ob.data.materials.clear();ob.data.materials.append(glass);ob['status']='conditional_old_lantern_topology_transparent_skin';ob['confidence_detail']='U unresolved exterior profile';ob['parameter_ids']='entry_package.json;reading_void.json'
  sol=ob.modifiers.new('Preview glass thickness','SOLIDIFY');sol.thickness=.014;sol.offset=0
  old.hide_render=True;old.hide_set(True);old['status']='superseded_by_P17_transparent_skin';replaced.append(old.name);made.append(ob.name)
S['stage']='P17 reading floor void and P15 glass-guard pilot; sloped ceiling remains unresolved';S['current_file']=out.name
camera_data=bpy.data.cameras.new('P17_READING_DETAIL');camera=bpy.data.objects.new('P17_READING_DETAIL',camera_data);root.objects.link(camera)
camera.location=xy([611,678])+up*(UP+2.7);target=center+up*(UP+.3);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=34;S.camera=camera
S.render.resolution_x=1500;S.render.resolution_y=1200;S.render.resolution_percentage=100
S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/P17_reading_void.png')
bpy.data.texts.new('P17_READING_NOTES').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),closed_objects=made,cutters=cutters,roof_boolean_targets=targets,replaced=replaced,floor_z=UP,center_world=list(center),floor_void_world=[list(p) for p in void],roof_void_world=[list(p) for p in roofvoid],construction_acceptance=False)
(B/'reports/P17_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('P17_SAVED',out)
