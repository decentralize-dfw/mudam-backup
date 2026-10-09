"""R42 containment and glass clearance, evaluated closed meshes and component counts."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R42_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();origin=Vector(r['roof_origin']);u=Vector(r['u']);v=Vector(r['v']);normal=Vector(r['normal']);fail=[];checks=[]
def in_convex(pt,poly,tol=1e-4):
 values=[(b[0]-a[0])*(pt[1]-a[1])-(b[1]-a[1])*(pt[0]-a[0]) for a,b in zip(poly,poly[1:]+poly[:1])];return min(values)>=-tol or max(values)<=tol
for row in r['shading_arrays']:
 ob=bpy.data.objects[row['name']];parent=bpy.data.objects[row['parent_glass']];n=len(parent.data.vertices)//2;world=[parent.matrix_world@p.co for p in list(parent.data.vertices)[:n]];poly=[((p-origin).dot(u),(p-origin).dot(v)) for p in world];ev=ob.evaluated_get(deps);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);volume=bm.calc_volume(signed=True);nonmanifold=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);remaining=set(bm.verts);components=0
 while remaining:
  stack=[remaining.pop()];components+=1
  while stack:
   vv=stack.pop()
   for edge in vv.link_edges:
    other=edge.other_vert(vv)
    if other in remaining:remaining.remove(other);stack.append(other)
 outside=0;depths=[]
 for vv in me.vertices:
  p=ob.matrix_world@vv.co-origin;outside+=not in_convex((p.dot(u),p.dot(v)),poly);depths.append(-p.dot(normal))
 check=dict(name=ob.name,volume=volume,nonmanifold=nonmanifold,zero_faces=zero,components=components,expected_slats=row['slat_count'],outside_parent=outside,glass_clearance_range_m=[min(depths),max(depths)]);checks.append(check)
 if volume<=0 or nonmanifold or zero or outside or components!=row['slat_count'] or min(depths)<.1 or max(depths)>.16:fail.append(check)
 bm.free();ev.to_mesh_clear()
result=dict(file=r['file'],arrays=checks,slat_count=sum(c['components'] for c in checks),failures=fail,construction_acceptance=False);(B/'reports/R42_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(arrays=len(checks),slats=result['slat_count'],failures=fail),indent=2));assert not fail,fail
