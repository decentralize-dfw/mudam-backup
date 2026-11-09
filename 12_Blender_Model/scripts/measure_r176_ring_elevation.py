from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();a=Vector((66.1472,397.0413));b=Vector((195.2534,508.9011));u=(b-a).normalized();n=Vector((u.y,-u.x));out=[]
for t in [.25,.5,.75]:
 p=a.lerp(b,t);levels=[]
 for z in np.arange(5,36,.5):
  q=p+n*25;hit,h,normal,*_=bpy.context.scene.ray_cast(dg,Vector((q.x,q.y,z)),Vector((-n.x,-n.y,0)),distance=45)
  if hit:levels.append([float(z),round((Vector((h.x,h.y))-p).dot(n),3)])
 out.append(dict(t=t,levels=levels));print(t,levels)
(R/'reports/R176_ANNEAU_FACADE_SECTIONS.json').write_text(json.dumps(out,indent=2))
