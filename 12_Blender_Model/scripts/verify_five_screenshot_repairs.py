from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R95_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));fail=[];results=[];solids=[]
def tree(names):
 vs=[];fs=[]
 for name in names:
  o=bpy.data.objects[name];off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in f.vertices) for f in o.data.polygons)
 return BVHTree.FromPolygons(vs,fs,epsilon=0.00001)
for name in r['closed_objects']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);row=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),volume=bm.calc_volume(signed=True));bm.free();solids.append(row)
 if row['nonmanifold'] or row['volume']<=0:fail.append(row)
for p in r['probes']:
 t=tree([p['object']]);a=Vector(p['point']);n=Vector(p['normal']);hit=t.ray_cast(a+n*.7,-n,1.4)[0] is not None;good=hit==(p['expected']=='closed');results.append(dict(**p,hit=hit,passed=good))
 if not good:fail.append(results[-1])
t=tree([n for n in r['closed_objects'] if n.startswith('R95_EAST_')]);samples=0
for f in r['glazed_surfaces']:
 ps=[Vector(p) for p in f['vertices']];n=Vector(f['normal'])
 for j in range(1,len(ps)-1):
  a,b,c=ps[0],ps[j],ps[j+1]
  for u in range(21):
   for v in range(21-u):
    q=a+(b-a)*(u/20)+(c-a)*(v/20);samples+=1
    if t.ray_cast(q+n*.2,-n,.4)[0] is None:fail.append(dict(surface=f['name'],miss=list(q)))
# Deliberately omit a seam pane at its centroid: prove the check can see the old opening.
f=r['glazed_surfaces'][4];ps=[Vector(p) for p in f['vertices']];a=sum(ps,Vector())/len(ps);n=Vector(f['normal']);own=tree([f['name']]);assert own.ray_cast(a+n*.2,-n,.4)[0] is not None
if bpy.data.objects.get('R28_W_DETACHED_ENTRY_WALL'):fail.append('West detached wall unexpectedly restored')
q=dict(file=r['file'],failures=fail,solids=solids,local_probes=results,glazing_samples=samples,construction_acceptance=False,limits=r['limits']);(B/'reports/R95_verification.json').write_text(json.dumps(q,indent=2));print('R95',len(results),'targeted probes',samples,'glass samples',len(fail),'failures');assert not fail
