import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();cx,cy=-71.05941,-47.59488;rows=[]
for z in [-1,0,1,2,3]:
 for deg in range(0,360,3):
  t=math.radians(deg);di=Vector((math.cos(t),math.sin(t),0));h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((cx,cy,z)),di,distance=7)
  if h:rows.append(dict(z=z,angle=deg,x=p.x,y=p.y,r=math.hypot(p.x-cx,p.y-cy),normal=list(n),radialNormal=float(n.dot(di))))
(R/'reports/R573_WEST_TOWER_FACE_CONTROLS.json').write_text(json.dumps(rows,indent=2));print('controls',len(rows),flush=True)
