import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'reports/R538_NORTH_WALL_CAP.json').read_text());line=[Vector(p)for p in d['line']];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for seg in [0,2]:
 a,b=line[seg:seg+2];t=(b-a).normalized();n=Vector((-t.y,t.x))
 for frac in [.3,.5,.7,.9]:
  q=a+(b-a)*frac;hits=[]
  for k in range(-10,21):
   off=k*.1;xy=q+n*off;hit,p,no,i,o,m=bpy.context.scene.ray_cast(dg,Vector((xy.x,xy.y,20)),Vector((0,0,-1)),distance=50)
   if hit:hits.append(dict(offset=off,z=p.z,nz=no.z))
  rows.append(dict(segment=seg,t=frac,hits=hits));print(seg,frac,[(round(h['offset'],1),round(h['z'],2),round(h['nz'],1))for h in hits],flush=True)
(R/'reports/R538_CAP_SECTIONS.json').write_text(json.dumps(rows,indent=2))
