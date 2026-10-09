"""R72 reopened wall coverage, area-bearing seams and roof protrusion checks."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R72_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));up=Vector((0,0,1));fail=[];coverage=[];seams=[];roofchecks=[];solids=[];deps=bpy.context.evaluated_depsgraph_get()
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def tree(name):
 o=bpy.data.objects[name].evaluated_get(deps);me=o.to_mesh();t=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);o.to_mesh_clear();return t
for name in r['closed_objects']:
 o=bpy.data.objects[name]
 if o.hide_render:continue
 bm=bmesh.new();bm.from_mesh(o.data);q=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),volume=bm.calc_volume(signed=True),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['nonmanifold'] or q['volume']<=0 or q['zero_faces']:fail.append(q)
t=tree('R72_LOWER_FOYER_NORTH_WALL');normal=(point(0,1)-point(0,0)).normalized()
for i in range(1,52):
 for j in range(1,12):
  x=462+130*i/52;z=r['lower_z']+(0-r['lower_z'])*j/12;origin=point(x,325,z);hit=t.ray_cast(origin,normal,2)
  q=dict(x=x,z=z,passed=hit[0] is not None);coverage.append(q)
  if not q['passed']:fail.append(q)
# Check the inherited lower wall mid-thickness is supported by the new upper
# envelope at the actual horizontal joint, not only a shared zero-area edge.
for side in [3,5]:
 new=tree(f'R72_HIGH_ATRIUM_WALL_{side}');old_names=[q['name'] for q in r['trimmed_lower_walls'] if (q['name']=='P05_MAIN_ATRIUM_BASE_3' if side==3 else q['name'].startswith('P05_MAIN_ATRIUM_BASE_5'))]
 for name in old_names:
  o=bpy.data.objects[name];vs=[o.matrix_world@v.co for v in o.data.vertices];tops=[v for v in vs if abs(v.z-r['join_z'])<1e-4];center=sum(tops,Vector())/len(tops)
  for v in tops:
   sample=center.lerp(v,.8);sample.z=r['join_z']-.02;hit=new.ray_cast(sample,up,.1);q=dict(lower_wall=name,passed=hit[0] is not None);seams.append(q)
   if not q['passed']:fail.append(q)
roof=[tree(o.name) for o in bpy.context.scene.objects if o.name.startswith('P06_MAIN_ROOF_FACE_')]
for d in r['definitions']:
 if 'HIGH_ATRIUM' not in d['name']:continue
 new=tree(d['name']);p=[Vector(v) for v in d['polygon_canonical']]
 for i in range(21):
  for j in range(5):
   a=p[0].lerp(p[1],(i+.1)/21);b=p[3].lerp(p[2],(i+.1)/21);xy=a.lerp(b,(j+.1)/5);origin=point(*xy,35);hit=new.ray_cast(origin,-up,30)
   rh=[h[0].z for t in roof if (h:=t.ray_cast(point(*xy,0),up,40))[0] is not None]
   if hit[0] is None:fail.append(dict(missing_wall_top=d['name'],sample=list(xy)));continue
   protrusion=hit[0].z-min(rh) if rh else None;q=dict(wall=d['name'],canonical=list(xy),protrusion_m=protrusion,passed=protrusion is None or protrusion<.003);roofchecks.append(q)
   if not q['passed']:fail.append(q)
result=dict(file=r['file'],solids=solids,basement_coverage=coverage,area_contact_seams=seams,roof_protrusion_checks=roofchecks,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R72_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R72',len(coverage),'coverage',len(seams),'seams',len(roofchecks),'roof samples',len(fail),'failures');assert not fail,fail[:10]
