from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R103_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));fail=[];rows=[]
for spec in r['trims']:
 ob=bpy.data.objects[spec['name']];bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world);z=[min(v.co.z for v in bm.verts),max(v.co.z for v in bm.verts)]
 distance=min((v.co-Vector(spec['plane_point'])).dot(Vector(spec['outward'])) for v in bm.verts) if 'plane_point' in spec else 0
 row=dict(name=ob.name,volume=abs(bm.calc_volume(signed=True)),nonmanifold=sum(not e.is_manifold for e in bm.edges),minimum_plane_distance=distance,z=z)
 if row['nonmanifold'] or not 0<row['volume']<spec['volume_before'] or row['minimum_plane_distance']<-.00003 or max(abs(a-b) for a,b in zip(z,spec['before_z']))>.00003:fail.append(row)
 rows.append(row);bm.free()
q=json.loads((B/'reports/R103_upper_gallery_inner_faces.json').read_text());assert q['file']==r['file'];fail.extend(q['findings'])
deep=json.loads((B/'reports/R103_upper_gallery_deep_faces.json').read_text());assert deep['file']==r['file'];fail.extend(deep['findings'])
before=json.loads((B/'reports/R102_upper_gallery_inner_faces.json').read_text());result=dict(file=r['file'],solids=rows,source_face_checks=q['checks'],before_findings=len(before['findings']),after_findings=len(q['findings']),failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R103_verification.json').write_text(json.dumps(result,indent=2));print(len(rows),'solids',q['checks'],'face checks',len(fail),'failures');assert not fail
