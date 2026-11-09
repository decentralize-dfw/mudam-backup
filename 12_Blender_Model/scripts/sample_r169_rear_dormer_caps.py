from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';quads=[[(170,815),(510,730),(550,890),(210,975)],[(800,660),(1110,580),(1140,740),(830,820)]]
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in tr.vertices] for tr in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);out=[]
for q in quads:
 pts=[]
 for u in np.linspace(.15,.85,6):
  for v in np.linspace(.15,.85,6):
   px=(1-v)*((1-u)*np.array(q[0])+u*np.array(q[1]))+v*((1-u)*np.array(q[3])+u*np.array(q[2]));x,y=-68.10883331298828+(px[0]-700)/175,-293.02964782714844+(700-px[1])/175;h,*_=tree.ray_cast(Vector((x,y,50)),Vector((0,0,-1)),200)
   if h is not None:pts.append(tuple(h))
 p=np.array(pts);A=np.c_[p[:,:2],np.ones(len(p))];c=np.linalg.lstsq(A,p[:,2],rcond=None)[0];err=A@c-p[:,2];out.append(dict(pixels=q,plane=c.tolist(),samples=len(p),rmse=float(np.sqrt(np.mean(err**2))),p90=float(np.percentile(abs(err),90))))
(D/'row_rear_dormer_cap_trials.json').write_text(json.dumps(out,indent=2));print('ROOF_FIELDS',out,flush=True)

