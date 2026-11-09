import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();corners=json.loads((R/'reports/R468_STRIP_CROSS_VALIDATION.json').read_text())['outline'];a,b,c,d=map(Vector,corners);pts=[]
for u in [.15,.35,.5,.65,.85]:
 for v in [.1,.25,.4,.55,.7,.85,.95]:
  p=a.lerp(b,u).lerp(d.lerp(c,u),v);h,q,n,*_=bpy.context.scene.ray_cast(dg,Vector((p.x,p.y,15)),Vector((0,0,-1)),distance=40)
  if h:pts.append(dict(u=u,v=v,position=list(q),normal=list(n)))
(R/'reports/R489_STRIP_RAYS.json').write_text(json.dumps(pts,indent=2));print([(p['u'],p['v'],round(p['position'][2],3),round(p['normal'][2],2)) for p in pts])
