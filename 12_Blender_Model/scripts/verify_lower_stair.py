"""R05 saved-file checks, including source opening and upper/lower circulation."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R05_build_report.json').read_text());P=json.loads((B/'config/lower_stair.json').read_text());args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];r['file']=args[0] if args else r['file'];report_name=args[1] if len(args)>1 else 'R05_verification.json';bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
for name in r['closed_objects']+[r['changed_floor']]:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);v=bm.calc_volume(signed=True);nm=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free();ob.to_mesh_clear();solids.append(dict(name=name,volume=v,nonmanifold=nm,zero_faces=zero))
 if v<=0 or nm or zero:fail.append(solids[-1])
center=Vector(r['center_world']);ex=Vector(r['canonical_x_world']);ey=Vector(r['canonical_y_world']);up=Vector((0,0,1));LOW=r['lower_z'];RI=r['inner_radius'];RO=r['outer_radius'];A=r['bottom_angle'];d=r['opening_chord_difference_canonical'];scale=json.loads((B/'config/foundation.json').read_text())['calibration']['meters_per_canonical_pixel'];cx,cy=P['center_canonical']
def end(rad):return math.acos((d-(cx-cy))*scale/(rad*math.sqrt(2)))-math.pi/4
def point(t,rad,z):
 a=A+(end(rad)-A)*t;return center+(ex*math.cos(a)+ey*math.sin(a))*rad+up*z
visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def ray(origin,direction,distance,only=None):
 hits=[]
 for ob in visible:
  if only and ob.name not in only:continue
  inv=ob.matrix_world.inverted();hit,loc,_,_=ob.ray_cast(inv@origin,inv.to_3x3()@direction,distance=distance)
  if hit:
   world=ob.matrix_world@loc;hits.append(dict(name=ob.name,distance=(world-origin).length,z=world.z))
 return sorted(hits,key=lambda h:h['distance'])
walk=[];underside=[];eyes=[]
for step in r['steps']:
 t=(step['t0']+step['t1'])/2
 for f in [.2,.5,.8]:
  p=point(t,RI+(RO-RI)*f,step['top']);support=ray(p+up*.025,-up,.06);head=ray(p+up*.025,up,2);ok=bool(support) and support[0]['name']==step['name'] and not head;walk.append(dict(tread=step['name'],fraction=f,support=support[:2],head=head,passed=ok))
  if not ok:fail.append(dict(test='walk_support_headroom',tread=step['name'],fraction=f,support=support,head=head))
  if f==.5:eyes.append(p+up)
 if step['bottom']>LOW+.05:
  p=point(t,(RI+RO)/2,step['bottom']-.025);hits=ray(p,up,.06,only=[step['name']]);ok=bool(hits) and abs(hits[0]['z']-step['bottom'])<1e-4;underside.append(dict(tread=step['name'],hits=hits,passed=ok))
  if not ok:fail.append(dict(test='stepped_underside',tread=step['name'],hits=hits))
transitions=[]
for a,b in zip(eyes,eyes[1:]):
 hits=ray(a,(b-a).normalized(),(b-a).length);transitions.append(hits)
 if hits:fail.append(dict(test='eye_path',hits=hits))
floor_support=[]
for f in [.2,.5,.8]:
 rad=RI+(RO-RI)*f;a=end(rad);tangent=(-ex*math.sin(a)+ey*math.cos(a)).normalized();p=point(1,rad,.05)+tangent*.25;hits=ray(p,-up,.1,only=[r['changed_floor']]);ok=bool(hits) and abs(hits[0]['z'])<1e-4;floor_support.append(dict(kind='upper_exit',fraction=f,hits=hits,passed=ok))
 if not ok:fail.append(floor_support[-1])
 p=point(0,rad,LOW+.05)-(-ex*math.sin(A)+ey*math.cos(A))*.25;hits=ray(p,-up,.1,only=['P05_ZONE_LM1_GALLERIES_FOYER']);ok=bool(hits) and abs(hits[0]['z']-LOW)<1e-4;floor_support.append(dict(kind='lower_entry',fraction=f,hits=hits,passed=ok))
 if not ok:fail.append(floor_support[-1])
for j,coords in enumerate(r['ground_guard_support_points']):
 p=Vector(coords);p.z=.06;hits=ray(p,-up,.12,only=[r['changed_floor']]);ok=bool(hits) and abs(hits[0]['z'])<1e-4;floor_support.append(dict(kind='ground_guard',index=j,hits=hits,passed=ok))
 if not ok:fail.append(floor_support[-1])
# Reject the old full semicircular hole: the central peninsula must have floor.
for dx,dy in [(0,0),(6,-6),(-6,6)]:
 p=center+ex*dx*scale+ey*dy*scale;p.z=.05;hits=ray(p,-up,.1,only=[r['changed_floor']]);ok=bool(hits);floor_support.append(dict(kind='retained_peninsula',offset=[dx,dy],hits=hits,passed=ok))
 if not ok:fail.append(floor_support[-1])
# The remote corner beyond the stair arc is an open light well, not a floor cap.
p=center+ex*(675-cx)*scale+ey*(350-cy)*scale;p.z=.05;hits=ray(p,-up,.1,only=[r['changed_floor']]);ok=not hits;floor_support.append(dict(kind='corner_void',hits=hits,passed=ok))
if not ok:fail.append(floor_support[-1])
# Check the rail's actual circular cross sections perpendicular to the helix.
round_checks=[]
for side,rad in [('INNER',RI),('OUTER',RO)]:
 ob=bpy.data.objects['R05_ROUND_RAIL_'+side];points=[ob.matrix_world@v.co for v in ob.data.vertices];error=0.;plane=0.
 for j in range(161):
  t=j/160;a=A+(end(rad)-A)*t;c=point(t,rad,LOW+t*(-LOW)+P['railing_height_m']);tangent=(-ex*math.sin(a)*rad+ey*math.cos(a)*rad+up*((-LOW)/(end(rad)-A))).normalized()
  for v in points[j*20:(j+1)*20]:error=max(error,abs((v-c).length-P['rail_diameter_m']/2));plane=max(plane,abs((v-c).dot(tangent)))
 round_checks.append(dict(side=side,max_radius_error_m=error,max_section_plane_error_m=plane))
 if error>1e-4 or plane>1e-4:fail.append(round_checks[-1])
assert bpy.data.objects[r['changed_floor']].modifiers['GH_down_void'].object.name=='R05_SOURCE_GROUND_OPENING'
assert all(bpy.data.objects[n].hide_render for n in r['cutters'])
assert abs(r['steps'][0]['top']-LOW-r['rise_m'])<1e-8 and abs(r['steps'][-1]['top']+r['rise_m'])<1e-8
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,walk_support_headroom=walk,stepped_underside_checks=underside,eye_path_rays=transitions,floor_support=floor_support,round_rail_checks=round_checks,risers_candidate=r['risers_candidate'],real_riser_count_verified=False,metric_photo_pose_verified=False,construction_acceptance=False)
(B/'reports'/report_name).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2));assert not fail,fail
