"""Reopen R108; compare joint coverage to saved R107 vertices."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R108_build_report.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
trees={};oldtrees={};fail=[];solids=[];rays=[];preserved=[];up=Vector((0,0,1))
for name in r['closed_objects']:
 ob=bpy.data.objects[name];vs=[ob.matrix_world@v.co for v in ob.data.vertices];fs=[list(f.vertices) for f in ob.data.polygons]
 trees[name]=BVHTree.FromPolygons(vs,fs);oldtrees[name]=BVHTree.FromPolygons([Vector(v) for v in r['before_world_vertices'][name]],fs)
 bm=bmesh.new();bm.from_mesh(ob.data);row=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),signed_volume=bm.calc_volume(signed=True));bm.free();solids.append(row)
 if row['nonmanifold'] or row['zero_faces'] or row['signed_volume']<=0:fail.append(row)
 allowed=[Vector(c['old'][j['parts'].index(name)]) for j in r['joints'] if name in j['parts'] for c in j['corners']]
 bad=[];moved=0
 for i,(old,new) in enumerate(zip(r['before_world_vertices'][name],vs)):
  old=Vector(old)
  if (old-new).length<2e-5:continue
  moved+=1
  if abs(old.z-new.z)>2e-5 or not any((old.xy-p.xy).length<2e-5 for p in allowed):bad.append(i)
 preserved.append(dict(name=name,moved_vertices=moved,unexpected_changed_vertices=bad))
 if bad or not moved:fail.append(preserved[-1])
for j in r['joints']:
 p=Vector(j['center'])
 for c in j['corners']:
  a,b=map(Vector,c['old']);m=Vector(c['miter'])
  for sample in [(p+a+m)/3,(p+b+m)/3]:
   q=Vector((sample.x,sample.y,-.1));before=[];after=[]
   for name in j['parts']:
    if oldtrees[name].ray_cast(q,up,4.6)[0] is not None:before.append(name)
    if trees[name].ray_cast(q,up,4.6)[0] is not None:after.append(name)
   row=dict(source_corner=j['source_corner'],position=list(q),before=before,after=after);rays.append(row)
   if not after:fail.append(row)
  for name in j['parts']:
   error=min(((bpy.data.objects[name].matrix_world@v.co).xy-m.xy).length for v in bpy.data.objects[name].data.vertices)
   if error>2e-5:fail.append(dict(name=name,seam_error=error))
result=dict(file=r['file'],solids=solids,preservation=preserved,corner_samples=rays,previously_open_samples=sum(not x['before'] for x in rays),failures=fail,construction_acceptance=False)
(B/'reports/R108_verification.json').write_text(json.dumps(result,indent=2))
print('R108',len(rays),'samples',result['previously_open_samples'],'old misses',len(fail),'failures');assert not fail,fail
