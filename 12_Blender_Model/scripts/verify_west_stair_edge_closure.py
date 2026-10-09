"""R88 reopened panel planes, solids and the four previously uncovered vertical rays."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R88_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));C=json.loads((B/'config/foundation.json').read_text())['calibration'];fail=[];solids=[];trees={}
for item in r['panels']:
 o=bpy.data.objects[item['name']];bm=bmesh.new();bm.from_mesh(o.data);q=dict(name=o.name,volume_m3=bm.calc_volume(signed=True),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges));bm.free();ps=[o.matrix_world@v.co for v in o.data.vertices];n=Vector(item['normal']);a=Vector(item['source_polygon'][0]);deviations=[abs((p-a).dot(n)) for p in ps];q['plane_error_m']=max(min(abs(d),abs(d-.018)) for d in deviations);solids.append(q)
 if q['volume_m3']<=0 or q['nonmanifold_edges'] or q['plane_error_m']>1e-4:fail.append(q)
 trees[o.name]=BVHTree.FromPolygons(ps,[list(p.vertices) for p in o.data.polygons])
import math
before=json.loads((B/'reports/R88_before_stair_findings.json').read_text());rays=[]
for row in before['findings']:
 for ray in row['escapes']:
  pos=Vector(row['position'])+Vector((0,0,ray['z']));a=math.radians(ray['angle']);d=Vector((math.cos(a),math.sin(a),0));hits=[name for name,t in trees.items() if t.ray_cast(pos,d,200)[0] is not None];item=dict(step=row['step'],fraction=row['fraction'],hits=hits);rays.append(item)
  if not hits:fail.append(item)
q=dict(file=r['file'],solids=solids,previous_joint_misses=rays,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R88_verification.json').write_text(json.dumps(q,indent=2));print('R88',len(solids),'panels',len(fail),'failures');assert not fail,fail
