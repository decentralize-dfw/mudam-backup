import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));eye=Vector((90,-105,55));f=(Vector((28,-36,-3))-eye).normalized();rot=f.to_track_quat('-Z','Y');r=rot@Vector((1,0,0));u=rot@Vector((0,1,0));dg=bpy.context.evaluated_depsgraph_get();points=[]
for px in range(430,551,10):
 for offset in [10,20,30]:
  py=515+(px-430)*.3+offset;origin=eye+r*((px/800-.5)*75)+u*((.5-py/680)*63.75);h,p,n,*_=bpy.context.scene.ray_cast(dg,origin,f,distance=250)
  if h and n.y<-.65 and n.z<.65:points.append(list(p))
q=np.array(points);A=np.c_[q[:,0],q[:,2],np.ones(len(q))];test=np.arange(len(q))%4==0;c=np.linalg.lstsq(A[~test],q[~test,1],rcond=None)[0];e=A[test]@c-q[test,1];d=dict(points=points,planeYfromXZ=c.tolist(),heldout=int(test.sum()),training=int((~test).sum()),rms=float(np.sqrt(np.mean(e*e))),max=float(abs(e).max()),accepted=False);(R/'reports/R494_WALL_FACE_PLANE.json').write_text(json.dumps(d,indent=2));print({k:v for k,v in d.items() if k!='points'})
