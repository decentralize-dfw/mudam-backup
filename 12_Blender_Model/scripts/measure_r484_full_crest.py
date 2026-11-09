import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();pts=[]
for y in np.arange(14,44.01,.5):
 x=y-69.8;h,p,*_=s.ray_cast(dg,Vector((x,y,20)),Vector((0,0,-1)),distance=50)
 if h:pts.append([x,float(y),p.z])
q=np.array(pts);test=np.arange(len(q))%3==0;A=np.c_[np.ones(len(q)),q[:,1]-30];c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];e=A[test]@c-q[test,2];out=dict(controls=pts,axis='x=y-69.8',extentY=[24,39],crest=c.tolist(),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(e*e))),max=float(abs(e).max()),widthM=1.4,widthBasis='Oblique/top source visual estimate, not surveyed. Crest axis source trace; independent planar wall geometry planned.');(R/'reports/R484_NW_WALL_FULL_CREST.json').write_text(json.dumps(out,indent=2));print(out)

