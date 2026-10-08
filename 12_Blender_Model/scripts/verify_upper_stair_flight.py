"""Saved R04: closed volumes, tread support, headroom, exit and prior local openings."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R04_build_report.json').read_text());P=json.loads((B/'config/upper_stair_flight.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Q=json.loads((B/'config/stair_glass_return.json').read_text())
report_path=B/'reports/R04_verification.json'
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:];assert len(args)==2;r['file']=args[0];report_path=B/'reports'/args[1]
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
for name in r['closed_objects']+[r['modified_floor']]:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);v=bm.calc_volume(signed=True);nm=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free();ob.to_mesh_clear();solids.append(dict(name=name,volume=v,nonmanifold=nm,zero_faces=zero))
 if v<=0 or nm or zero:fail.append(solids[-1])
def xy(p):
 k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+off[0];v=k*p[1]+off[1]
 return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def ray(origin,direction,distance,only=None):
 hits=[]
 for ob in visible:
  if only and ob.name not in only:continue
  inv=ob.matrix_world.inverted();hit,loc,_,_=ob.ray_cast(inv@origin,inv.to_3x3()@direction,distance=distance)
  if hit:
   world=ob.matrix_world@loc;hits.append(dict(name=ob.name,distance=(world-origin).length,point=list(world)))
 return sorted(hits,key=lambda t:t['distance'])
walk=[];eyes=[];up=Vector((0,0,1))
for step in r['steps']:
 a=xy([(step['outer0'][i]+step['outer1'][i])/2 for i in range(2)]);b=xy([(step['inner0'][i]+step['inner1'][i])/2 for i in range(2)])
 for f in [.2,.5,.8]:
  p=a.lerp(b,f)+up*step['z'];support=ray(p+up*.03,-up,.10);head=ray(p+up*.03,up,2.0);ok=bool(support) and support[0]['name']==step['name'] and abs(support[0]['point'][2]-step['z'])<1e-4 and not head
  walk.append(dict(tread=step['name'],width_fraction=f,support=support[:2],headroom_hits=head,passed=ok))
  if not ok:fail.append(dict(test='walk_support_headroom',tread=step['name'],fraction=f,support=support,head=head))
  if f==.5:eyes.append(p+up)
transitions=[]
for a,b in zip(eyes,eyes[1:]):
 hits=ray(a,(b-a).normalized(),(b-a).length);transitions.append(hits)
 if hits:fail.append(dict(test='between_treads',hits=hits))
last=r['steps'][-1];p=eyes[-1];axis=(xy([501,501])-xy([500,500])).normalized();exit_hits=ray(p,axis,1.5)
if exit_hits:fail.append(dict(test='upper_exit',hits=exit_hits))
# Exact foot-return tube connection, with tolerance for float32 local vertices.
curve=bpy.data.objects['R03_RETURN_ROUND_HANDRAIL'];vertices=[curve.matrix_world@v.co for v in curve.data.vertices];center=sum(vertices[:20],Vector())/20;join_error=(center-Vector(r['return_connector_world'])).length
if join_error>1e-4:fail.append(dict(test='handrail_return_connection',error=join_error))
# Earlier open portal and recessed lamp must survive the larger stair recess.
old=json.loads((B/'reports/R02_build_report.json').read_text());a,b=map(Vector,old['portal_endpoints']);normal=Vector(old['normal']);portal=[]
for t in [.2,.5,.8]:
 for z,expected in [(1.2,False),(old['ground_clear']-.05,False),((old['ground_clear']+old['beam_top'])/2,True),(old['beam_top']+.2,False),(old['upper_head']-.2,False)]:
  p=a.lerp(b,t);p.z=z;hits=ray(p-normal*.5,normal,1);portal.append(dict(t=t,z=z,hits=hits))
  if bool(hits)!=expected:fail.append(dict(test='R02_portal',t=t,z=z,hits=hits))
old=json.loads((B/'reports/R03_build_report.json').read_text());center=Vector(old['center_world']);axis=Vector(old['axis_world']);normal=Vector(old['normal_world']);recess=[]
for radius,wanted,z_wanted in [(0,'R03_UPLIGHT_GLASS_LENS',old['lens_z']),(.30,'R03_RECESSED_STONE_DISH',old['recess_z']),(.57,'R03_PODIUM_3_WITH_RECESS',old['podium_top_z'])]:
 for a in [0,math.pi/2,math.pi,3*math.pi/2]:
  hits=ray(center+(normal*math.cos(a)+axis*math.sin(a))*radius+up*2,-up,3);ok=bool(hits) and hits[0]['name']==wanted and abs(hits[0]['point'][2]-z_wanted)<1e-4;recess.append(dict(radius=radius,angle=a,hits=hits,passed=ok))
  if not ok:fail.append(dict(test='R03_recess',radius=radius,angle=a,hits=hits))
assert all(bpy.data.objects[n].hide_render for n in r['cutters']+r['replaced'])
assert abs(r['steps'][-1]['z']-r['upper_level'])<1e-8
assert len([o for o in bpy.data.objects if o.name.startswith('P10_') and o.get('element_type')=='roof_glass_panel'])==359
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,walk_support_headroom=walk,between_tread_eye_rays=transitions,upper_exit_hits=exit_hits,return_rail_join_error_m=join_error,portal_regression=portal,recess_regression=recess,main_risers_candidate=r['main_risers_candidate'],metric_riser_count_verified=False,upper_plan_interpretation_verified=False,construction_acceptance=False)
report_path.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2));assert not fail,fail
