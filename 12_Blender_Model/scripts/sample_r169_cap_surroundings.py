from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_rear_dormer_cap_trials.json').read_text())[0];quad=np.array([[-68.10883331298828+(x-700)/175,-293.02964782714844+(700-y)/175] for x,y in d['pixels']]);bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in tr.vertices] for tr in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]
for u in [-.3,0,.25,.5,.75,1,1.3]:
 for v in [-.5,0,.5,1,1.5,2,2.5,3]:
  xy=(1-v)*((1-u)*quad[0]+u*quad[1])+v*((1-u)*quad[3]+u*quad[2]);h,*_=tree.ray_cast(Vector((xy[0],xy[1],50)),Vector((0,0,-1)),200)
  if h is not None:rows.append(dict(u=u,v=v,x=float(xy[0]),y=float(xy[1]),z=h.z,cap_residual=float(h.z-np.dot(d['plane'],[*xy,1]))))
(D/'row_cap_surrounding_sections.json').write_text(json.dumps(rows,indent=2))
for u in [-.3,0,.25,.5,.75,1,1.3]:print(u,[(r['v'],round(r['cap_residual'],3)) for r in rows if r['u']==u],flush=True)
