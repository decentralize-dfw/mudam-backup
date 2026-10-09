from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R78_build_report.json').read_text());P=json.loads((B/'config/ground_gallery_access.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];trees={};up=Vector((0,0,1))
def point(p,z=0):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for name in r['closed_objects']:
 o=bpy.data.objects[name];vs=[o.matrix_world@v.co for v in o.data.vertices];trees[name]=BVHTree.FromPolygons(vs,[list(f.vertices) for f in o.data.polygons]);bm=bmesh.new();bm.from_mesh(o.data);q=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),volume=bm.calc_volume(signed=True),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['nonmanifold'] or q['volume']<=0 or q['zero_faces']:fail.append(q)
def inside(p,poly):
 x,y=p;c=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:c=not c
 return c
faces=[];interior=[]
for side,poly in P['source_gallery_polygons'].items():
 tree=trees[f'R78_{side}_GROUND_GALLERY_WALL_BODY'];path=[poly[1],poly[0]] if side=='E' else [poly[1],poly[0],poly[-1],poly[-2],poly[-3],poly[-4]];center=sum((point(p) for p in poly),Vector())/len(poly)
 for edge,(aa,bb) in enumerate(zip(path,path[1:])):
  a,b=point(aa),point(bb);n=(b-a).normalized().cross(up)
  if n.dot((a+b)/2-center)<0:n=-n
  for f in [.05,.15,.3,.5,.7,.85,.95]:
   for z in [.4,1.5,3.9]:
    p=a.lerp(b,f)+up*z;hit=tree.ray_cast(p-n*.03,n,.06);q=dict(side=side,edge=edge,fraction=f,z=z,passed=hit[0] is not None);faces.append(q)
    if not q['passed']:fail.append(q)
 lo=[min(p[i] for p in poly) for i in [0,1]];hi=[max(p[i] for p in poly) for i in [0,1]]
 for i in range(1,30):
  for j in range(1,30):
   xy=[lo[0]+(hi[0]-lo[0])*i/30,lo[1]+(hi[1]-lo[1])*j/30]
   if not inside(xy,poly):continue
   hits=[name for name,t in trees.items() if t.ray_cast(point(xy,-.1),up,4.6)[0] is not None];q=dict(side=side,canonical=xy,hits=hits);interior.append(q)
   if hits:fail.append(q)
heads=[]
for t in json.loads((B/'reports/R14_build_report.json').read_text())['steps']:
 for f in [-.3,0,.3]:
  p=Vector(t['center'])+Vector(t['side'])*t['width']*f+up*.025;hits=[name for name,tree in trees.items() if tree.ray_cast(p,up,2.1)[0] is not None];q=dict(tread=t['name'],fraction=f,hits=hits);heads.append(q)
  if hits:fail.append(q)
q=dict(file=r['file'],solids=solids,source_face_samples=faces,room_interior_clearance=interior,west_stair_head_samples=heads,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R78_verification.json').write_text(json.dumps(q,indent=2),encoding='utf8');print('R78',len(faces),'source face samples',len(interior),'room interior samples',len(heads),'stair clearance',len(fail),'failures');assert not fail,fail
