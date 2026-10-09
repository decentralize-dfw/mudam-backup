from pathlib import Path
import bpy,bmesh,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R13_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];planes=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
for panel in r['panels']:
 ob=bpy.data.objects[panel['name']];n=len(ob.data.vertices)//2;vs=np.array([list(v.co) for v in ob.data.vertices]);top=vs[:n];normal=np.cross(top[1]-top[0],top[2]-top[0]);normal/=np.linalg.norm(normal);row=dict(name=ob.name,plane_error=float(max(abs((top-top[0])@normal))),thickness_error=float(max(abs(abs((vs[n:]-top)@normal)-.018))));planes.append(row)
 if row['plane_error']>2e-5 or row['thickness_error']>2e-5:fail.append(row)
facets=[]
for i,ps in enumerate(r['source_facets']):
 a=np.array(ps);n=np.cross(a[1]-a[0],a[2]-a[0]);n/=np.linalg.norm(n);err=float(max(abs((a-a[0])@n)));facets.append(err)
 if err>2e-5:fail.append(dict(facet=i,error=err))
assert all(bpy.data.objects[n].hide_render for n in r['hidden_superseded'])
# Every original stone eave corner must still occur on the roof source perimeter.
wall=bpy.data.objects['P04_PAV_WALL_ENVELOPE'];top=max(v.co.z for v in wall.data.vertices);eaves=[wall.matrix_world@v.co for v in wall.data.vertices if abs(v.co.z-top)<1e-4];roof=[Vector(p) for face in r['source_facets'] for p in face];joins=[min((p-q).length for q in roof) for p in eaves]
if max(joins)>1e-4:fail.append(dict(eave_max_error=max(joins)))
tower=[p for p in r['panels'] if p['name'].startswith('R13_LANTERN_')];assert len(tower)==36
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,glass_planes=planes,primary_facet_errors_m=facets,stone_eave_max_error_m=max(joins),tower_glass_count=len(tower),construction_acceptance=False);(B/'reports/R13_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),panels=len(planes),failures=fail),indent=2));assert not fail,fail
