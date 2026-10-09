from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R77_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];trees={};oldtrees={};fixed=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name];vs=[ob.matrix_world@v.co for v in ob.data.vertices];faces=[list(f.vertices) for f in ob.data.polygons];trees[name]=BVHTree.FromPolygons(vs,faces);oldtrees[name]=BVHTree.FromPolygons([Vector(v) for v in r['before_world_vertices'][name]],faces);bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),volume=bm.calc_volume(signed=True),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['nonmanifold'] or q['zero_faces'] or q['volume']<=0:fail.append(q)
 bad=[]
 for i,(a,b) in enumerate(zip(r['before_world_vertices'][name],vs)):
  if abs(a[2]-b.z)>2e-5 or (i not in r['allowed_vertex_indices'][name] and (Vector(a)-b).length>2e-5):bad.append(i)
 fixed.append(dict(name=name,unexpected_changes=bad))
 if bad:fail.append(fixed[-1])
p=Vector(r['shared_front']);m=Vector(r['shared_back']);n=(m-p).cross(Vector((0,0,1))).normalized();rays=[]
# Offsets follow each actual wall interior. Symmetric +/- seam normals would
# test the exterior of this concave/overlapping joint as though it were a butt joint.
for f in [.15,.3,.5,.7,.85]:
 for name in r['closed_objects']:
  ob=bpy.data.objects[name];center=sum((ob.matrix_world@v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices);center.z=0;sample=p.lerp(m,f);direction=(center-sample).normalized();a=sample+direction*.008;a.z=-.1
  before=[k for k,t in oldtrees.items() if t.ray_cast(a,Vector((0,0,1)),r['z_overlap'][1]+.2)[0] is not None];after=[k for k,t in trees.items() if t.ray_cast(a,Vector((0,0,1)),r['z_overlap'][1]+.2)[0] is not None];q=dict(fraction=f,interior_of=name,before=before,after=after,passed=name in after);rays.append(q)
  if not q['passed']:fail.append(q)
if not any(len(q['after'])==2 for q in rays):fail.append(dict(no_positive_area_overlap=True))
for name in r['closed_objects']:
 for key in ['shared_front','shared_back']:
  point=Vector(r[key]);err=min(Vector(((bpy.data.objects[name].matrix_world@v.co).x-point.x,(bpy.data.objects[name].matrix_world@v.co).y-point.y,0)).length for v in bpy.data.objects[name].data.vertices)
  if err>2e-5:fail.append(dict(name=name,key=key,error=err))
q=dict(file=r['file'],solids=solids,fixed_heights_and_unrelated_vertices=fixed,seam_area_rays=rays,previously_empty_samples=sum(not q['before'] for q in rays),failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R77_verification.json').write_text(json.dumps(q,indent=2),encoding='utf8');print('R77',len(rays),'seam area rays',len(fail),'failures');assert not fail,fail
