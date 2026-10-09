from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R68_build_report.json').read_text());P=json.loads((B/'config/pavilion_moat.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[];trees={}
def tree(name):
 if name not in trees:
  ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();trees[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);ob.to_mesh_clear()
 return trees[name]
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
# Source centreline and head rays must agree, not merely be closed meshes.
wall_checks=[]
for wall,seg in zip(r['walls'],P['segments']):
 a,b=Vector(wall['start']),Vector(wall['end']);sa,sb=[Vector((*q,0)) for q in seg['points']];error=max((a-sa).length,(b-sb).length);hits=[]
 for t in [.1,.3,.5,.7,.9]:
  p=a.lerp(b,t)+Vector((0,0,1));hit=tree(wall['name']).ray_cast(p,Vector((0,0,-1)),8);hits.append(None if hit[0] is None else hit[0].z)
 q=dict(wall=wall['name'],source_xy_error=error,heads=hits);wall_checks.append(q)
 if error>1e-6 or any(z is None or abs(z-P['wall_top_z'])>2e-5 for z in hits):fail.append(q)
sys.path.insert(0,str(Path(__file__).parent));from plan_union import inside
poly=P['polygon'];samples=[]
for i in range(41):
 for j in range(41):
  x=min(p[0] for p in poly)+(max(p[0] for p in poly)-min(p[0] for p in poly))*(i+.5)/41;y=min(p[1] for p in poly)+(max(p[1] for p in poly)-min(p[1] for p in poly))*(j+.5)/41
  if not inside([x,y],poly):continue
  p=tree('R68_MOAT_GROUND').ray_cast(Vector((x,y,0)),Vector((0,0,-1)),8)[0];q=dict(x=x,y=y,z=None if p is None else p.z);samples.append(q)
  if p is None or abs(p.z-P['ground_top_z'])>2e-5:fail.append(q)
collisions=[]
# Check below-ground pavilion room/stair geometry: the wedge must stay outside it.
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or not ob.name.startswith(('R17_','R25_')):continue
 for name in r['closed_objects']:
  n=len(tree(ob.name).overlap(tree(name)))
  if n:collisions.append(dict(existing=ob.name,new=name,intersections=n))
if collisions:fail.append(dict(pavilion_intersections=collisions))
result=dict(file=r['file'],closed_solids=solids,wall_source_checks=wall_checks,ground_samples=samples,pavilion_intersections=collisions,failures=fail,construction_acceptance=False,terrain_height_surveyed=False);(B/'reports/R68_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R68',len(solids),'solids',len(samples),'ground rays',len(fail),'failures');assert not fail,fail
