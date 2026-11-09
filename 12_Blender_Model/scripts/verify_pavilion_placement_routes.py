"""Compare visible floor support across pavilion placement; no scene mutation saved."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
fit=json.loads((R/'reports/R151_pavilion_registration_candidate.json').read_text())
shift=Vector((*fit['translation_xy'],0)); old=fit['old']
start=Vector((15.2,-27.5,0));end=Vector(((old[3][0]+old[4][0])/2,(old[3][1]+old[4][1])/2,0));axis=end-start
def transformed(p):
 t=max(0,min(1,(Vector((p.x,p.y,0))-start).dot(axis)/axis.length_squared))
 return p+shift*t
def trees():
 result=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or o.name.startswith('R151_ACT_'):continue
  if not any(s in o.name for s in ('FLOOR','TREAD','LANDING','STEP')):continue
  v=[o.matrix_world@p.co for p in o.data.vertices]
  if not v or min(p.x for p in v)>40 or max(p.x for p in v)<10 or min(p.y for p in v)>-20 or max(p.y for p in v)<-55:continue
  result.append((o.name,BVHTree.FromPolygons(v,[list(p.vertices) for p in o.data.polygons])))
 return result
def hit(ts,p):
 hits=[]
 for name,bvh in ts:
  loc,no,face,d=bvh.ray_cast(p+Vector((0,0,.3)),Vector((0,0,-1)),.65)
  if loc is not None:hits.append((name,loc.z))
 return hits
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v005.blend'))
before=trees();samples=[]
# Three tracks across link, including both endpoint joins. Compare existing support only.
side=Vector((-axis.y,axis.x,0)).normalized()
for i in range(121):
 for off in (-.45,0,.45):
  p=start+axis*(i/120)+side*off;p.z=0
  h=hit(before,p)
  if h:samples.append((p,h))
version='v011' if '--v011' in sys.argv else ('v010' if '--v010' in sys.argv else 'v009')
bpy.ops.wm.open_mainfile(filepath=str(R/f'scenes/MUDAM_R151_ACT_CEVRE_ADAY_{version}.blend'))
after=trees();rows=[];fail=[]
for p,h in samples:
 q=transformed(p);a=hit(after,q)
 row=dict(before_point=list(p),after_point=list(q),before=h,after=a);rows.append(row)
 if not a:
  near=[]
  for name,bvh in after:
   loc,no,face,d=bvh.find_nearest(q)
   if loc is not None and d<.001:near.append(dict(name=name,distance=d,point=list(loc)))
  row['boundary_nearest_within_1mm']=near
  if not near:fail.append(row)
 elif abs(max(z for _,z in a)-max(z for _,z in h))>.02:fail.append(row)
report=dict(scope='Three link tracks at original upper floor Z; support and elevation comparison only. Not complete stair/headroom acceptance.',samples=len(rows),failures=fail,rows=rows)
(R/f'reports/R151_{version}_link_support.json').write_text(json.dumps(report,indent=2))
print('LINK_SUPPORT',len(rows),'FAILURES',len(fail),flush=True)
