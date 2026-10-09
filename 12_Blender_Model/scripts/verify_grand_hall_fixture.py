from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R50_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];checks=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();checks.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
anchor_checks=[]
for a in r['anchors']:
 ob=bpy.data.objects[a['parent']];end=Vector(a['end']);distance=min((ob.matrix_world@v.co-end).length for v in ob.data.vertices);q=dict(name=a['name'],parent=ob.name,contact_distance_m=distance,length_m=(end-Vector(a['start'])).length);anchor_checks.append(q)
 if distance>1e-5 or end.z<=a['start'][2] or ob.hide_render:fail.append(q)
expected={(gx+dx,gy+dy) for gx,gy in [(0,-2),(2,0),(0,2),(-2,0)] for dx,dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]};actual={tuple(x['lattice']) for x in r['lights']}
if actual!=expected or len(r['lights'])!=20:fail.append('Wrong observed cylinder topology')
# Clearance between separate housing exteriors, independent of their shared supports.
centers=[Vector(x['center']) for x in r['lights']];gap=min((a-b).length for i,a in enumerate(centers) for b in centers[i+1:])-.36
if gap<.19:fail.append(dict(housing_gap=gap))
result=dict(file=r['file'],closed_mesh_checks=checks,anchors=anchor_checks,cylinder_count=len(actual),minimum_housing_clearance_m=gap,failures=fail,limits='Topology and local model contact only. No real suspension load/path, elevation or physical dimensions accepted.',construction_acceptance=False);(B/'reports/R50_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(objects=len(checks),lights=len(actual),failures=fail)));assert not fail,fail
