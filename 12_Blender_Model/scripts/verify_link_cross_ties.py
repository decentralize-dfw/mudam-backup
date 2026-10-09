from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R65_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();trees={};fail=[];solids=[];rays=[];crossings=[]
def tree(name):
 if name not in trees:
  ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();trees[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);ob.to_mesh_clear()
 return trees[name]
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
for q in r['support_rays']:
 p,n,i,d=tree(q['portal']).ray_cast(Vector(q['origin']),Vector((0,0,-1)),q['max_distance']);row=dict(portal=q['portal'],origin=q['origin'],hit=list(p) if p else None,distance=d);rays.append(row)
 if p is None:fail.append(row)
for i in range(r['bays']):
 a,b=r['ties'][i*2:i*2+2];gap=abs(a['crossing_z']-b['crossing_z'])-2*r['rod_radius_m'];overlap=tree(a['rod']).overlap(tree(b['rod']));row=dict(bay=i,surface_gap_m=gap,triangle_intersections=len(overlap));crossings.append(row)
 if gap<.005 or overlap:fail.append(row)
# Axial shanks are required to connect the fork pin to the barrel; inspect actual bounds along each tie.
connections=[]
for tie in r['ties']:
 for e in tie['ends']:
  prefix=e['terminal_prefix'];pairs=[('_TONGUE','_PIN'),('_TONGUE','_BARREL'),('_BARREL','_NECK')]
  for a,b in pairs:
   hit=tree(prefix+a).overlap(tree(prefix+b));row=dict(a=prefix+a,b=prefix+b,intersecting_triangles=len(hit));connections.append(row)
   # The neck is partially contained axially and overlaps barrel caps; touching surfaces are deliberate.
   if not hit:fail.append(row)
result=dict(file=r['file'],solids=solids,support_rays=rays,crossings=crossings,terminal_connections=connections,failures=fail,construction_acceptance=False,limits='Geometric assembly and separated X rods only. Not structural sizing, force or as-built connection certification.');(B/'reports/R65_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R65 solids',len(solids),'support',len(rays),'connections',len(connections),'fail',len(fail));assert not fail,fail
