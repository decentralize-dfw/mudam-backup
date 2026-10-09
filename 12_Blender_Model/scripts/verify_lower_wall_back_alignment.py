from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R104_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));ob=bpy.data.objects[r['object']];vs=[ob.matrix_world@v.co for v in ob.data.vertices];fail=[];p=Vector(r['plane_point']);n=Vector(r['plane_normal']);back=r['back_indices']
for i,v in enumerate(vs):
 old=Vector(r['before_world'][i])
 if abs(v.z-old.z)>1e-5 or (i not in back and (v-old).length>1e-5):fail.append(dict(index=i,unexpected_motion=True))
 if i in back and abs((v-p).dot(n))>1e-5:fail.append(dict(index=i,unmatched_face=True))
bm=bmesh.new();bm.from_mesh(ob.data);solid=dict(volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges));bm.free()
if solid['volume']<=0 or solid['nonmanifold']:fail.append(solid)
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
touch=tree(ob).overlap(tree(bpy.data.objects[r['neighbor']]))
if not touch:fail.append('wall joint lost')
q=dict(file=r['file'],solid=solid,aligned_vertices=len(back),fixed_vertices=len(vs)-len(back),wall_joint_intersections=len(touch),failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R104_verification.json').write_text(json.dumps(q,indent=2));print(q);assert not fail
