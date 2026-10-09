from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R91_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));o=bpy.data.objects[r['closed_objects'][0]];ps=[o.matrix_world@v.co for v in o.data.vertices];bm=bmesh.new();bm.from_mesh(o.data);fail=[]
solid=dict(volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges));bm.free()
if solid['volume']<=0 or solid['nonmanifold']:fail.append(solid)
tree=BVHTree.FromPolygons(ps,[list(f.vertices) for f in o.data.polygons]);a,b=map(Vector,r['roof_endpoints']);edge=b-a;n=Vector((-edge.y,edge.x,0)).normalized();rows=[]
for i in range(1,200):
 p=a.lerp(b,i/200)
 for dz in [-.15,0,.1]:
  q=p+Vector((0,0,dz));hit=tree.ray_cast(q+n*.5,-n,1);row=dict(fraction=i/200,offset=dz,wall_hit=hit[0] is not None);rows.append(row)
  if hit[0] is None:fail.append(row)
for idx in [0,1,4,5]:
 if abs(ps[idx].z-r['before_vertices'][idx][2])>1e-6:fail.append(dict(changed_base=idx))
for idx,expected in [(3,a.z+.2),(7,a.z+.2),(2,b.z+.2),(6,b.z+.2)]:
 if abs(ps[idx].z-expected)>1e-5:fail.append(dict(top=idx))
q=dict(file=r['file'],solid=solid,joint_rays=rows,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R91_verification.json').write_text(json.dumps(q,indent=2));print('R91 joint rays',len(rows),'failures',len(fail));assert not fail,fail
