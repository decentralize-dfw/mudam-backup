from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R80_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];trees={};oldtrees={}
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for name in r['closed_objects']:
 ob=bpy.data.objects[name];vs=[ob.matrix_world@v.co for v in ob.data.vertices];faces=[list(f.vertices) for f in ob.data.polygons];trees[name]=BVHTree.FromPolygons(vs,faces);bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
 if name in r['before_world_vertices']:
  old=r['before_world_vertices'][name];oldtrees[name]=BVHTree.FromPolygons([Vector(p) for p in old],faces);zmin=min(p[2] for p in old)
  for i,(a,b) in enumerate(zip(old,vs)):
   if abs(a[0]-b.x)>2e-5 or abs(a[1]-b.y)>2e-5 or (a[2]>zmin+2e-5 and abs(a[2]-b.z)>2e-5):fail.append(dict(unexpected_vertex_change=name,index=i))
n=(point(575,335)-point(575,334)).normalized();rays=[]
for x in [558.5+i*.5 for i in range(67)]:
 for z in [.1,.4,.8,1.2,1.6,2.,2.4,2.8]:
  p=point(x,334,z)-n*.3;before=[name for name,t in oldtrees.items() if t.ray_cast(p,n,.6)[0] is not None];after=[name for name,t in trees.items() if t.ray_cast(p,n,.6)[0] is not None];q=dict(canonical_x=x,z=z,before_hits=before,after_hits=after,passed=bool(after));rays.append(q)
  if not after:fail.append(q)
q=dict(file=r['file'],solids=solids,lower_closure_rays=rays,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R80_verification.json').write_text(json.dumps(q,indent=2),encoding='utf8');print('R80',len(solids),'solids',len(rays),'closure rays',len(fail),'failures');assert not fail,fail
