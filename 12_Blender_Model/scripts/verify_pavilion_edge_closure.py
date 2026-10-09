"""R86 reopened panel planes, solids and the four previously uncovered vertical rays."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R86_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));C=json.loads((B/'config/foundation.json').read_text())['calibration'];fail=[];solids=[];trees={}
for item in r['panels']:
 o=bpy.data.objects[item['name']];bm=bmesh.new();bm.from_mesh(o.data);q=dict(name=o.name,volume_m3=bm.calc_volume(signed=True),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges));bm.free();ps=[o.matrix_world@v.co for v in o.data.vertices];n=Vector(item['normal']);a=Vector(item['source_polygon'][0]);deviations=[abs((p-a).dot(n)) for p in ps];q['plane_error_m']=max(min(abs(d),abs(d-.018)) for d in deviations);solids.append(q)
 if q['volume_m3']<=0 or q['nonmanifold_edges'] or q['plane_error_m']>1e-4:fail.append(q)
 trees[o.name]=BVHTree.FromPolygons(ps,[list(p.vertices) for p in o.data.polygons])
def point(x,y):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,1.2))
rays=[]
for y in [276,278,280,282]:
 hits=[name for name,t in trees.items() if t.ray_cast(point(139,y),Vector((0,0,1)),45)[0] is not None];q=dict(canonical=[139,y],hits=hits);rays.append(q)
 if not hits:fail.append(q)
q=dict(file=r['file'],solids=solids,previous_cover_misses=rays,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R86_verification.json').write_text(json.dumps(q,indent=2));print('R86',len(solids),'panels',len(fail),'failures');assert not fail,fail
