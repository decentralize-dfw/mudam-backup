from pathlib import Path
import bpy,json,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());vs=[];fs=[]
for r in d['meshes']:
 k=len(vs);vs.extend(r['vertices']);fs.extend([k+i for i in f] for f in r['faces'])
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);out=[]
for r in json.loads((R/'config/r191_boundary_domains.json').read_text()):
 samples=[];c=r['plane'];origin=r['origin']
 for ring in r['rings']:
  for aa,bb in zip(ring,ring[1:]+ring[:1]):
   a,b=Vector(aa),Vector(bb)
   for j in range(max(1,math.ceil((b-a).length))):
    p=a.lerp(b,j/max(1,math.ceil((b-a).length)));h=g.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),300)[0]
    if h:samples.append([p.x,p.y,c[0]*(p.x-origin[0])+c[1]*(p.y-origin[1])+c[2]-h.z])
 out.append(dict(name=r['name'],samples=samples,absolute_gap_p90=float(np.quantile(abs(np.array(samples)[:,2]),.9)),maximum_gap=float(max(abs(x[2]) for x in samples))))
(R/'reports/R191_EDGE_MEASUREMENTS.json').write_text(json.dumps(out,indent=2));print([(r['name'],r['absolute_gap_p90'],r['maximum_gap']) for r in out])
