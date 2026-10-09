"""Reopen R71 and independently check old gaps, miter continuity and fixed fronts."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R71_build_report.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];rays=[];trees={};oldtrees={};fixed=[];up=Vector((0,0,1))
for name in r['closed_objects']:
 ob=bpy.data.objects[name];vs=[ob.matrix_world@v.co for v in ob.data.vertices];faces=[list(f.vertices) for f in ob.data.polygons]
 trees[name]=BVHTree.FromPolygons(vs,faces);oldtrees[name]=BVHTree.FromPolygons([Vector(v) for v in r['before_world_vertices'][name]],faces)
 bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),signed_volume=bm.calc_volume(signed=True));bm.free();solids.append(q)
 if q['nonmanifold'] or q['zero_faces'] or q['signed_volume']<=0:fail.append(q)
 allowed=[]
 for j in r['joints']:
  if name in j['parts']:allowed.extend([Vector(j['old_back_a']),Vector(j['old_back_b'])])
 bad=[];kept=0
 for index,(a,b) in enumerate(zip(r['before_world_vertices'][name],vs)):
  a=Vector(a)
  if (a-b).length<2e-5:kept+=1;continue
  if abs(a.z-b.z)>2e-5 or not any(Vector((a.x-p.x,a.y-p.y,0)).length<2e-5 for p in allowed):bad.append(index)
 fixed.append(dict(name=name,unchanged_vertices=kept,unexpected_changed_vertices=bad))
 if bad:fail.append(fixed[-1])
for j in r['joints']:
 p,a,b,m=[Vector(j[k]) for k in ['inner','old_back_a','old_back_b','shared_back']]
 z0,z1=j['z_overlap'];assert z1>z0
 # Two samples inside the two added triangles, offset from their common seam.
 for sample in [(p+a+m)/3,(p+m+b)/3]:
  if min((sample-p).length,(sample-m).length)<1e-6:continue
  before=[];after=[]
  origin=Vector((sample.x,sample.y,z0-.2))
  for name in j['parts']:
   for container,tree in [(before,oldtrees[name]),(after,trees[name])]:
    hit=tree.ray_cast(origin,up,z1-z0+.4)
    if hit[0] is not None:container.append(name)
  q=dict(level=j['level'],side=j['side'],corner=j['corner'],point=list(sample),before_hits=before,after_hits=after,passed=bool(after));rays.append(q)
  if not q['passed']:fail.append(q)
 # Both adjacent backs must now have the same XY endpoint at some elevation.
 for name in j['parts']:
  ob=bpy.data.objects[name];error=min(Vector(((ob.matrix_world@v.co).x-m.x,(ob.matrix_world@v.co).y-m.y,0)).length for v in ob.data.vertices)
  if error>2e-5:fail.append(dict(name=name,corner=j['corner'],seam_error=error))
result=dict(file=r['file'],solids=solids,front_and_height_preservation=fixed,junction_rays=rays,previously_open_samples=sum(not q['before_hits'] for q in rays),failures=fail,construction_acceptance=False)
(B/'reports/R71_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R71',len(solids),'walls',len(rays),'rays',result['previously_open_samples'],'old gap samples',len(fail),'failures');assert not fail,fail
