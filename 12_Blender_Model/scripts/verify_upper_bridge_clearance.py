from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R98_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];probes=[]
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/r['base_scene']));ob=bpy.data.objects['R45_STAIR_RECESS_CONTINUOUS'];me=ob.data;me.calc_loop_triangles();z=r['upper_z']+.9
M=C['pdf_to_utm_matrix'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def cy(p):
 dx=p.x+293425-M[0][2];dy=p.y+5499960-M[1][2];return ((-M[1][0]*dx+M[0][0]*dy)/det-C['canonical_to_pdf_offset'][1])/C['canonical_to_pdf_scale']
for face in me.loop_triangles:
 ps=[ob.matrix_world@me.vertices[i].co for i in face.vertices];hits=[]
 for a,b in zip(ps,ps[1:]+ps[:1]):
  if a.z<z<=b.z or b.z<z<=a.z:hits.append(a.lerp(b,(z-a.z)/(b.z-a.z)))
 if len(hits)==2 and min(cy(p) for p in hits)>556 and (hits[0]-hits[1]).length>1e-6:
  pa,pb=hits;n=(pb-pa).cross(Vector((0,0,1))).normalized();probes.append((pa.lerp(pb,.5),n))
assert probes;checks={}
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));vs=[];fs=[]
 for name in r['closed_objects']:
  o=bpy.data.objects[name];off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons)
 t=BVHTree.FromPolygons(vs,fs);rows=[]
 for a,n in probes:
  hit=t.ray_cast(a+n*.4,-n,.8)[0]
  # A probe close to the source boundary can touch the correctly retained end cap.
  canonical_y=None
  if hit is not None:
   M=C['pdf_to_utm_matrix'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0];dx=hit.x+293425-M[0][2];dy=hit.y+5499960-M[1][2];canonical_y=((-M[1][0]*dx+M[0][0]*dy)/det-C['canonical_to_pdf_offset'][1])/C['canonical_to_pdf_scale']
  rows.append(dict(point=list(a),hit_y=canonical_y,passed=hit is None or canonical_y<=r['source_boundary_y']+.0001))
 checks[phase]=rows
fail=[p for p in checks['after'] if not p['passed']];q=dict(file=r['file'],checks=checks,before_failures=sum(not x['passed'] for x in checks['before']),failures=fail,construction_acceptance=False);assert q['before_failures']>0;(B/'reports/R98_verification.json').write_text(json.dumps(q,indent=2));print('R98 bridge probes',len(probes),'before',q['before_failures'],'after',len(fail));assert not fail
