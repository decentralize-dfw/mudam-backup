from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R63_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();O,U,N=map(Vector,[r['origin'],r['axis'],r['outward']]);Z=Vector((0,0,1));fail=[];solids=[];trees={}
def tree(name):
 if name not in trees:
  ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();trees[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);ob.to_mesh_clear()
 return trees[name]
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(q);bm.free();ob.to_mesh_clear()
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
supports=[]
for label,x,d,z,expected,normal,maxdistance in [('inner',-1.15,-.035,1.55,'P12_CORNER_POST_-1_BACK',N,.02),('outer',-1.15,2.165,1.45,'P12_CORNER_POST_-1_FRONT',N,.02),('sign_left',-.09,.01,4.08,'P08_VESTIBULE_TOP_GLASS',Z,.04),('sign_right',.09,.01,4.08,'P08_VESTIBULE_TOP_GLASS',Z,.04)]:
 p,no,ix,dist=tree(expected).ray_cast(O+U*x+N*d+Z*z,normal,maxdistance);q=dict(label=label,target=expected,hit=list(p) if p else None,distance=dist);supports.append(q)
 if p is None:fail.append(q)
collisions=[];leaves=json.loads((B/'reports/P12_build_report.json').read_text())['leaf_families']
for name in r['closed_objects']:
 for f in leaves:
  for other in f['objects']:
   if tree(name).overlap(tree(other)):collisions.append(dict(device=name,leaf=other))
fail.extend(collisions)
result=dict(file=r['file'],solids=solids,support_rays=supports,current_pose_door_intersections=collisions,failures=fail,construction_acceptance=False,limits='Current candidate door pose only; not complete operating sweep or verified mechanism. Dimensions and device function remain unmeasured.');(B/'reports/R63_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R63 solids',len(solids),'supports',len(supports),'collisions',len(collisions),'failures',len(fail));assert not fail,fail
