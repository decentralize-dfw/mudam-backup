from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/bridge_full_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);d=json.loads((R/'reports/R175_BRIDGE_MEASUREMENTS.json').read_text());a=np.array(d['a']);u=np.array(d['u']);n=np.array(d['n']);hits=[]
for z in [-52,-54,-56,-58,-60]:
 runs=[];run=[]
 for s in np.arange(20,160,.2):
  p=a+u*s+n*20;h,no,*_=bvh.ray_cast(Vector((*p,z)),Vector((*(-n),0)),40);valid=h is not None and abs(np.dot(np.array(h[:2])-a-u*s,n)-5.2)<.65 and abs(no.x*n[0]+no.y*n[1])>.65
  if valid:run.append(float(s))
  elif run:runs.append([run[0],run[-1]]);run=[]
 if run:runs.append([run[0],run[-1]])
 hits.append(dict(z=z,runs=[r for r in runs if r[1]-r[0]>.4]))
(R/'reports/R305_BRIDGE_PIER_INTERVALS.json').write_text(json.dumps(hits,indent=2));print(hits)
