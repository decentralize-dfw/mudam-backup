"""Reopen R84 and test previous fixed-entry floor escapes and preserved geometry."""
from pathlib import Path
import runpy,json,sys,math,bpy,bmesh
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R84_build_report.json').read_text());old=json.loads((B/'reports/ENCLOSURE_BOUNDARY_DIAGNOSTIC.json').read_text());sys.argv=['audit','--',r['file']];g=runpy.run_path(str(B/'scripts/audit_interior_enclosure.py'));fail=[];solids=[];rays=[]
for n in r['closed_objects']:
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);q=dict(name=n,volume_m3=bm.calc_volume(signed=True),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges));bm.free();solids.append(q)
 if q['volume_m3']<=0 or q['nonmanifold_edges']:fail.append(q)
 for v,oldv in zip(o.data.vertices,r['before_world_vertices'][n]):
  p=o.matrix_world@v.co
  if abs(p.x-oldv[0])>1e-5 or abs(p.y-oldv[1])>1e-5:fail.append(dict(name=n,plan_changed=True))
for item in old:
 f=item['finding']
 if f['region']!='ENT':continue
 a=math.radians(f['angle']);d=Vector((math.cos(a),math.sin(a),0));h=g['tree'].ray_cast(g['point'](f['canonical'],f['z']),d,200);q=dict(**f,closure_hit=None if h[0] is None else g['names'][g['owners'][h[2]]]);rays.append(q)
 if h[0] is None:fail.append(q)
q=dict(file=r['file'],solids=solids,replayed_previous_escapes=rays,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R84_verification.json').write_text(json.dumps(q,indent=2));print('R84',len(solids),'solids',len(rays),'rays',len(fail),'failures');assert not fail,fail
