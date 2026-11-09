import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
src=BVHTree.FromPolygons(vs,fs,all_triangles=True);out=[]
for d in json.loads((R/'config/r289_roof_boundaries.json').read_text()):
 p=np.array(d['polygon']);center=p.mean(axis=0);samples=[]
 for j,a in enumerate(p):
  b=p[(j+1)%len(p)]
  if j in d['unresolvedCropEdges']:continue
  for t in np.linspace(.05,.95,31):
   edge=a+(b-a)*t;inside=center-edge;inside/=np.linalg.norm(inside)
   for dist in [.5,1.,2.]:
    xy=edge+inside*dist;h,n,*_=src.ray_cast(Vector((*xy,150)),Vector((0,0,-1)),200)
    z=np.dot([*(xy-np.array(d['origin'])),1],d['plane'])
    samples.append(dict(xy=xy.tolist(),inset=dist,edge=j,model=float(z),source=float(h.z) if h else None,error=float(abs(h.z-z)) if h else None))
 e=[s['error'] for s in samples if s['error'] is not None]
 out.append(dict(name=d['name'],samples=samples,summary=dict(count=len(e),missing=sum(s['source'] is None for s in samples),p90=float(np.percentile(e,90)),maximum=max(e),within25cm=float(np.mean(np.array(e)<.25)))))
(R/'reports/R289_BOUNDARY_SOURCE.json').write_text(json.dumps(out,indent=2));print([o['summary'] for o in out],flush=True)
