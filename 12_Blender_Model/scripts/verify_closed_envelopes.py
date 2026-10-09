from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R44_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];checks=[]
for row in r['surfaces']:
 ob=bpy.data.objects[row['name']];ev=ob.evaluated_get(deps);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);vs=[ev.matrix_world@v.co for v in me.vertices];front=[Vector(p) for p in row['original_front_world']];delta=Vector(row['extrusion_world']);error=max(min((p-v).length for v in vs) for p in front);back_error=max(min((p+delta-v).length for v in vs) for p in front);q=dict(name=ob.name,front_vertex_error_m=error,back_vertex_error_m=back_error,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));checks.append(q)
 if error>1e-5 or back_error>1e-5 or q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
 bm.free();ev.to_mesh_clear()
result=dict(file=r['file'],checks=checks,failures=fail,construction_acceptance=False);(B/'reports/R44_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(checked=len(checks),failures=fail),indent=2));assert not fail,fail
