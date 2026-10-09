from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R52_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();fail=[];checks=[];rays=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();checks.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero']:fail.append(q)
def cast(p,d,dist):
 hits=[]
 for ob in S.objects:
  if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
  eo=ob.evaluated_get(deps);inv=eo.matrix_world.inverted();hit,loc,_,_=eo.ray_cast(inv@p,inv.to_3x3()@d,distance=dist)
  if hit:
   world=eo.matrix_world@loc;hits.append(((world-p).length,ob.name,list(world)))
 return min(hits) if hits else None
for w in r['windows']:
 a,b,n=Vector(w['left']),Vector(w['right']),Vector(w['outward'])
 for t in [.15,.5,.85]:
  for z in [.5,1.5,2.8]:
   p=a.lerp(b,t)-n*.4+Vector((0,0,z));hit=cast(p,n,1);q=dict(bay=w['bay'],fraction=t,z=z,kind='inside_to_glass',hit=hit);rays.append(q)
   if not hit or hit[1]!=w['glass']:fail.append(q)
  p=a.lerp(b,t)-n*.25+Vector((0,0,1.65));hit=cast(p,Vector((0,0,-1)),2);q=dict(bay=w['bay'],fraction=t,kind='interior_floor',hit=hit);rays.append(q)
  if not hit or abs(hit[2][2])>.02:fail.append(q)
outward=[]
for w in r['windows']:
 a,b,n=Vector(w['left']),Vector(w['right']),Vector(w['outward'])
 for t in [.15,.5,.85]:
  p=a.lerp(b,t)+n*.2+Vector((0,0,1.65));outward.append(dict(bay=w['bay'],fraction=t,hit=cast(p,n,7)))
result=dict(file=r['file'],closed_mesh_checks=checks,rays=rays,outward_diagnosis=outward,failures=fail,visual_acceptance=False,construction_acceptance=False);(B/'reports/R52_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(closed=len(checks),rays=len(rays),outward=outward,failures=fail),indent=2))
