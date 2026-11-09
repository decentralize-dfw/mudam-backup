from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/bridge_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);a=np.array([-259.01,-288.315]);b=np.array([-181.285,-350.445]);u=(b-a)/np.linalg.norm(b-a);n=np.array([u[1],-u[0]]);rows=[]
for s in np.arange(-10,111,2):
 for d in np.arange(-7,7.01,.5):
  p=a+u*s+n*d;h,normal,*_=bvh.ray_cast(Vector((*p,100)),Vector((0,0,-1)),300)
  if h:rows.append([float(s),float(d),float(h.z),float(normal.z)])
(R/'reports/R175_BRIDGE_MEASUREMENTS.json').write_text(json.dumps({'a':a.tolist(),'u':u.tolist(),'n':n.tolist(),'length':float(np.linalg.norm(b-a)),'samples':rows}));print('DECK',np.quantile([r[2] for r in rows if abs(r[1])<2],[.1,.5,.9]))
