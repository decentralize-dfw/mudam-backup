from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];R=B.parent;sys.path.insert(0,str(B/'scripts'));from plan_union import inside
r=json.loads((B/'reports/R132_build_report.json').read_text());name='R38_PARK_APPROACH_GROUND';fail=[]
def read(path,names):
 bpy.ops.wm.open_mainfile(filepath=str(path));rows=[];trees=[]
 for n in names:
  o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);rows.append(dict(name=n,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),top_area=sum(f.calc_area() for f in bm.faces if f.normal.z>.99)));trees.append(BVHTree.FromBMesh(bm));bm.free()
 return rows,trees
before,bt=read(B/'scenes'/r['base_scene'],[name]);after,at=read(R/r['file'],[name]+r['closed_objects'])
for q in after:
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
if abs(sum(q['volume'] for q in after)-before[0]['volume'])>.002:fail.append('volume coverage changed')
samples=0;changed=0;overlap=0;misclassified=0
for x in range(-20,90):
 for y in range(-20,100):
  p=Vector((x+.317,y+.419,2));b=bt[0].ray_cast(p,Vector((0,0,-1)),4)[0];hits=[t.ray_cast(p,Vector((0,0,-1)),4)[0] for t in at];h=[v for v in hits if v is not None];samples+=1
  if (b is None)!=(not h) or (b is not None and any((v-b).length>1e-4 for v in h)):changed+=1
  if len(h)>1:overlap+=1
  if hits[1] is not None and not inside((p.x,p.y),r['woodland_polygon']):misclassified+=1
if changed or overlap or misclassified:fail.append(dict(coverage=changed,double_top=overlap,outside_source=misclassified))
result=dict(file=r['file'],solids=after,source_top_area_m2=before[0]['top_area'],woodland_top_area_m2=after[1]['top_area'],samples=samples,coverage_changes=changed,double_tops=overlap,outside_source=misclassified,failures=fail,construction_acceptance=False)
(B/'reports/R132_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result);assert not fail
