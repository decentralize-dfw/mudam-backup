from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_rear_dormer_cap_trials.json').read_text())[0];q=np.array([[-68.10883331298828+(x-700)/175,-293.02964782714844+(700-y)/175] for x,y in d['pixels']]);bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def xy(u,v):return (1-v)*((1-u)*q[0]+u*q[1])+v*((1-u)*q[3]+u*q[2])
def hit(x,y):
 h,*_=tree.ray_cast(Vector((float(x),float(y),50)),Vector((0,0,-1)),200);assert h is not None;return list(h)
verts=[hit(*xy(u,v)) for v in np.linspace(1,3,9) for u in np.linspace(0,1,9)];faces=[];err=[]
for j in range(8):
 for i in range(8):
  k=j*9+i
  for f in [(k,k+1,k+10),(k,k+10,k+9)]:
   faces.append(f);p=np.mean([verts[a] for a in f],axis=0);h=hit(*p[:2]);err.append(abs(h[2]-p[2]))
r=dict(vertices=verts,faces=faces,source_samples=81,independent_checks=128,p90=float(np.percentile(err,90)),maximum=max(err),accepted=False);(D/'row_transition_grid.json').write_text(json.dumps(r,indent=2));print('TRANSITION',r['p90'],r['maximum'],flush=True)
