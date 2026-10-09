from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R66_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();trees={};fail=[];solids=[];connections=[];lenses=[]
def tree(name):
 if name not in trees:
  ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();trees[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);ob.to_mesh_clear()
 return trees[name]
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
def connected(a,b):
 n=len(tree(a).overlap(tree(b)));q=dict(a=a,b=b,intersections=n);connections.append(q)
 if not n:fail.append(q)
for beam in r['beams']:
 for i in range(9):connected(beam,f'R18_LINK_TRANSVERSE_{i}')
for f in r['fixtures']:
 for a,b in [(f['stub'],f['beam']),(f['stub'],f['body']),(f['body'],f['lens']),(f['body'],f['cap'])]:connected(a,b)
 start=Vector(f['center'])-Vector((0,0,.25));hits=[]
 for name in [f['body'],f['lens'],f['cap']]:
  p,n,i,d=tree(name).ray_cast(start,Vector((0,0,1)),.30)
  if p is not None:hits.append((d,name,p.z))
 hit=min(hits) if hits else None;q=dict(id=f['id'],first_hit=hit);lenses.append(q)
 if hit is None or hit[1]!=f['lens'] or abs(hit[2]-(f['center'][2]-.107))>2e-5:fail.append(q)
result=dict(file=r['file'],solids=solids,connections=connections,lens_rays=lenses,failures=fail,construction_acceptance=False,limits='Contact and visibility checks only; fixture count/diameter and structural profiles remain candidates.');(B/'reports/R66_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R66',len(solids),'solids',len(connections),'connections',len(lenses),'lens rays',len(fail),'failures');assert not fail,fail
