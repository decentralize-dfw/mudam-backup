from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/station_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
polys=[('EAST_ENTRANCE',[(1100,790),(1255,778),(1460,850),(1500,970),(1145,1030)]),('EAST_UPPER',[(1060,480),(1225,470),(1260,780),(1100,790)]),('SOUTH_WALK',[(565,1128),(1145,1015),(1160,1080),(580,1190)]),('WEST_APRON',[(350,440),(450,445),(490,625),(335,610)])]
for name,px in polys:
 xy=np.array([[-345+x*110/1600,290-y*110/1600] for x,y in px]);center=xy.mean(0);sample=[]
 for p in xy:
  for t in [.2,.4,.6,.8]:
   q=p*t+center*(1-t);hit,h,n,*_=bpy.context.scene.ray_cast(dg,Vector((*q,50)),Vector((0,0,-1)),distance=150)
   if hit and n.z>.8 and h.z<0:sample.append([*q,h.z])
 a=np.array(sample);X=np.c_[a[:,:2]-center,np.ones(len(a))];c=np.linalg.lstsq(X,a[:,2],rcond=None)[0];err=abs(X@c-a[:,2]);rows.append(dict(name=name,xy=xy.tolist(),plane=c.tolist(),origin=center.tolist(),p90=float(np.quantile(err,.9)),samples=sample));print(name,c,np.quantile(err,.9))
(R/'config/r178_apron_planes.json').write_text(json.dumps(rows,indent=2))
