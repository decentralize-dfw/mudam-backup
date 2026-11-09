import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=json.loads((R/'reports/R495_RETURN_PROFILE.json').read_text());A=Vector(D['start']);B=Vector(D['end']);t=(B-A).normalized();n=Vector((-t.y,t.x));bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for s in [3,8,13,18]:
 hits=[]
 for j in range(-40,31):
  off=j*.1;q=A+t*s+n*off;h,p,no,i,o,m=bpy.context.scene.ray_cast(dg,Vector((q.x,q.y,35)),Vector((0,0,-1)),distance=80)
  if h:hits.append(dict(offset=off,z=p.z,nz=no.z))
 rows.append(dict(s=s,hits=hits));print(s,[(round(h['offset'],1),round(h['z'],2),round(h['nz'],1))for h in hits if -3<h['z']<0],flush=True)
(R/'reports/R529_RETURN_CAP_SECTIONS.json').write_text(json.dumps(rows,indent=2))
