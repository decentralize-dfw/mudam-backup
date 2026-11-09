import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'reports/R534_RUIN_WALL_DESIGN.json').read_text());line=[Vector(p[:2])for p in d['stations']];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for seg in [0,5]:
 a,b=line[seg:seg+2];t=(b-a).normalized();n=Vector((-t.y,t.x))
 for k in range(1,20):
  s=k/20;q=a+(b-a)*s
  for off in [-.65,-1,-1.35,-1.7]:
   xy=q+n*off;hit,p,no,i,o,m=bpy.context.scene.ray_cast(dg,Vector((xy.x,xy.y,20)),Vector((0,0,-1)),distance=50)
   if hit:rows.append(dict(segment=seg,t=s,offset=off,xy=list(xy),z=p.z,nz=no.z))
(R/'reports/R535_MOAT_SECTIONS.json').write_text(json.dumps(rows,indent=2));print([(r['segment'],r['t'],r['offset'],round(r['z'],2),round(r['nz'],2))for r in rows],flush=True)
