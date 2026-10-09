from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R58_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));dep=bpy.context.evaluated_depsgraph_get();fail=[];solids=[];support=[];glass=[];contact=[];up=Vector((0,0,1));deck=bpy.data.objects['R34_APPROACH_CONTINUOUS_DECK'].evaluated_get(dep);col=bpy.data.objects['P07_CORNER_SUPPORT_ENVELOPE'].evaluated_get(dep)
def hit(ob,p,d,length):
 iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@p,iv.to_3x3()@d,distance=length);return ok,list(ob.matrix_world@loc) if ok else None
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
 bm.free()
 if name.startswith(('R58_POST_','R58_BASE_CHANNEL_')):
  vs=[ob.matrix_world@v.co for v in ob.data.vertices];foot=[v for v in vs if abs(v.z)<1e-5]
  for v in foot:
   ok,loc=hit(deck,v+up*.015,-up,.03);q=dict(name=name,foot=list(v),supported=ok);support.append(q)
   if not ok:fail.append(q)
for run in r['guard_runs']:
 a,b=Vector(run['start']),Vector(run['end']);axis=(b-a).normalized();normal=axis.cross(up).normalized();ok,loc=hit(col,a+axis*.02+up*run['rail_center_z'],-axis,.08);q=dict(way=run['way'],column_hit=ok,location=loc,osmpoint_to_column_shift_m=run['attachment_shift_m']);contact.append(q)
 if not ok:fail.append(q)
 for name in run['glass_names']:
  ob=bpy.data.objects[name];c=sum((ob.matrix_world@v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices);ok,loc=hit(ob,c+normal*.05,-normal,.1);channel=bpy.data.objects[name.replace('GLASS','BASE_CHANNEL')];okbase,base=hit(channel,c+up*.02,-up,.5);q=dict(name=name,glass_hit=ok,channel_hit=okbase);glass.append(q)
  if not ok or not okbase:fail.append(q)
 for name in run['tube_names']:
  ob=bpy.data.objects[name];top=max((ob.matrix_world@v.co).z for v in ob.data.vertices)
  if abs(top-run['top_z'])>1e-5:fail.append(dict(name=name,wrong_top=top))
for name in r['changed_inherited_objects']:
 o=bpy.data.objects[name]
 if not o.hide_render or not o.hide_get():fail.append(dict(old_guard_visible=name))
result=dict(file=r['file'],closed_solids=solids,foot_support_samples=support,glass_and_channel_checks=glass,column_contacts=contact,failures=fail,construction_acceptance=False);(B/'reports/R58_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),supports=len(support),panels=len(glass),contacts=contact,failures=fail),indent=2));assert not fail,fail
