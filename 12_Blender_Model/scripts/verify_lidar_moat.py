"""R150 local terrain/bridge and preserved wall-head verification."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];R=B.parent;sys.path.insert(0,str(B/'scripts'));from plan_union import inside
r=json.loads((B/'reports/R150_build_report.json').read_text());p=json.loads((B/'.local_source_cache/r150_terrain_filtered.json').read_text());fail=[];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));trees={};solids=[]
for name in r['changed_inherited_objects']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);q=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),volume=bm.calc_volume(signed=True));solids.append(q);trees[name]=BVHTree.FromBMesh(bm);bm.free()
 if q['nonmanifold'] or q['zero_faces'] or q['volume']<=0:fail.append(q)
source_errors=[]
for row in p['surfaces']:
 o=bpy.data.objects[row['name']]
 for i,v in enumerate(row['vertices']):
  err=(o.matrix_world@o.data.vertices[i].co-Vector(v)).length
  if err>2e-5:source_errors.append(dict(name=o.name,vertex=i,error=err))
 if source_errors:fail.append('source mesh mismatch')
bridge=json.loads((B/'reports/R34_build_report.json').read_text())['union_boundary'];samples=0;penetrations=[];covered=0
for ix in range(math.floor(min(v[0] for v in bridge)*4),math.ceil(max(v[0] for v in bridge)*4)):
 for iy in range(math.floor(min(v[1] for v in bridge)*4),math.ceil(max(v[1] for v in bridge)*4)):
  x,y=(ix+.371)/4,(iy+.413)/4
  if not inside((x,y),bridge):continue
  samples+=1;hit=trees['R35_MOAT_GROUND'].ray_cast(Vector((x,y,2)),Vector((0,0,-1)),20)[0]
  if hit is not None:
   covered+=1
   if hit.z>-.4+1e-4:penetrations.append(dict(x=x,y=y,z=hit.z))
if penetrations:fail.append(dict(terrain_above_bridge_underside=len(penetrations)))
wall_fail=[];original=json.loads((B/'.local_source_cache/r150_existing_wall_meshes.json').read_text())
for row in r['wall_base_extensions']:
 old=next(x for x in original if x['name']==row['name']);o=bpy.data.objects[row['name']]
 for i,v in enumerate(old['vertices']):
  actual=o.matrix_world@o.data.vertices[i].co;expected=Vector(v)
  if abs(v[2]-row['old_base'])<1e-4:expected.z=row['new_base']
  if (actual-expected).length>2e-5:wall_fail.append(dict(name=o.name,vertex=i))
 if [list(f.vertices) for f in o.data.polygons]!=old['faces']:wall_fail.append(dict(name=o.name,issue='topology changed'))
if wall_fail:fail.append(wall_fail)
result=dict(file=r['file'],solids=solids,source_vertex_failures=source_errors,wall_preservation_failures=wall_fail,bridge_plan_samples=samples,terrain_below_bridge_samples=covered,bridge_penetrations=penetrations,failures=fail,construction_acceptance=False,limits=['Regional source-based terrain candidate; up to 9.27m source gaps interpolated.','National-to-model datum conditional, historic wall foundations unmeasured.','This does not certify whole-site terrain or all building intersections.'])
(B/'reports/R150_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(samples=samples,covered=covered,penetrations=len(penetrations),failures=fail),indent=2));assert not fail
