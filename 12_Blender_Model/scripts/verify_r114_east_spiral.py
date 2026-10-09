"""R10 saved-scene headroom through every helical tread and source floor joins."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R10_build_report.json').read_text());output='R114_R10_regression.json'
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:];r['file']=json.loads((B/'reports'/args[0]).read_text())['file'];output=args[1]
r['file']=json.loads((B/'reports/R114_build_report.json').read_text())['file'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
for name in sorted(set(r['closed_objects']+[r['changed_upper_floor']])):
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();ob.to_mesh_clear()
center=Vector(r['center_world']);ex=Vector(r['canonical_x_world']);ey=Vector(r['canonical_y_world']);up=Vector((0,0,1));RI=r['inner_radius'];RO=r['outer_radius'];UP=r['upper_z'];visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def polar(a,rad,z):return center+(ex*math.cos(a)+ey*math.sin(a))*rad+up*z
def ray(p,d,length,only=None):
 hits=[]
 for ob in visible:
  if only and ob.name not in only:continue
  inv=ob.matrix_world.inverted();ok,loc,_,_=ob.ray_cast(inv@p,inv.to_3x3()@d,distance=length)
  if ok:hits.append(dict(name=ob.name,distance=(ob.matrix_world@loc-p).length))
 return sorted(hits,key=lambda h:h['distance'])
walk=[];eyes=[];under=[]
for step in r['steps']:
 a=(step['a']+step['b'])/2
 for f in [.2,.5,.8]:
  p=polar(a,RI+(RO-RI)*f,step['top']+.025);support=ray(p,-up,.06);head=ray(p,up,2);ok=bool(support) and support[0]['name']==step['name'] and not head;row=dict(tread=step['name'],fraction=f,support=support[:2],head=head,passed=ok);walk.append(row)
  if not ok:fail.append(row)
  if f==.5:eyes.append(p+up)
 if step['bottom']>.025:
  p=polar(a,(RI+RO)/2,step['bottom']-.02);hits=ray(p,up,.05,only=[step['name']]);under.append(dict(tread=step['name'],hits=hits,passed=bool(hits)))
  if not hits:fail.append(under[-1])
paths=[]
for a,b in zip(eyes,eyes[1:]):
 hits=ray(a,(b-a).normalized(),(b-a).length);paths.append(hits)
 if hits:fail.append(dict(test='stair_eye_path',hits=hits))
landing=[]
for angle in [5,15,30,45,60,80]:
 p=polar(r['top_angle']+r['direction_sign']*math.radians(angle),(RI+RO)/2,UP+.03);support=ray(p,-up,.08,only=[r['changed_upper_floor']]);head=ray(p,up,2);row=dict(angle=angle,support=support,head=head,passed=bool(support) and not head);landing.append(row)
 if not row['passed']:fail.append(row)
for rad in [1.25,1.5,1.75,2,2.25,2.5]:
 p=polar(r['top_angle']+r['direction_sign']*math.pi/4,rad,UP+.03);support=ray(p,-up,.08,only=[r['changed_upper_floor']]);head=ray(p,up,2);row=dict(exit_radius=rad,support=support,head=head,passed=bool(support) and not head);landing.append(row)
 if not row['passed']:fail.append(row)
ground=[]
for f in [.2,.5,.8]:
 a=r['bottom_angle'];p=polar(a,RI+(RO-RI)*f,.03)-(-ex*math.sin(a)+ey*math.cos(a))*.25*r['direction_sign'];hits=ray(p,-up,.08,only=[r['changed_ground_floor']]);ground.append(dict(fraction=f,hits=hits,passed=bool(hits)))
 if not hits:fail.append(ground[-1])
assert all(bpy.data.objects[n].hide_render for n in r['hidden_superseded']+r['cutters'])
garden_sight=[]
scale=json.loads((B/'config/foundation.json').read_text())['calibration']['meters_per_canonical_pixel']
for height in [1,3,5]:
 p=center+ex*((429-308.7785908352882)*scale)+ey*((378-328.6980982209977)*scale)+up*1.65
 target=center+up*height;d=(target-p).normalized();hits=ray(p,d,(target-p).length-RO-.1)
 row=dict(height=height,hits=hits,passed=not hits);garden_sight.append(row)
 if hits:fail.append(dict(test='source034_open_garden_to_spiral',**row))
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,tread_support_headroom=walk,tread_eye_paths=paths,stepped_underside=under,upper_landing_exit=landing,lower_entry_support=ground,garden_sight=garden_sight,real_riser_count_verified=False,metric_photo_pose_verified=False,construction_acceptance=False);(B/'reports'/output).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
