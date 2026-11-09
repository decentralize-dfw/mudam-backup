import bpy,json,statistics,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get()
pixels=[(105,386),(502,163),(512,169),(694,516)];line=[Vector((-57+x*44/800,90-y*44/800))for x,y in pixels];rows=[]
for i,(a,b)in enumerate(zip(line,line[1:])):
 length=(b-a).length;t=(b-a).normalized();n=Vector((-t.y,t.x))
 for k in range(max(2,int(length/.6))):
  s=k/(max(2,int(length/.6))-1);q=a+(b-a)*s;hits=[]
  for off in [-.2,-.1,0,.1,.2]:
   p=q+n*off;hit,h,no,idx,o,m=bpy.context.scene.ray_cast(dg,Vector((p.x,p.y,20)),Vector((0,0,-1)),distance=50)
   if hit:hits.append(dict(offset=off,z=h.z,nz=no.z))
  rows.append(dict(segment=i,t=s,xy=list(q),hits=hits))
print([(r['segment'],round(r['t'],2),[(h['offset'],round(h['z'],2),round(h['nz'],1))for h in r['hits']])for r in rows],flush=True)
(R/'reports/R538_NORTH_WALL_CAP.json').write_text(json.dumps(dict(pixels=pixels,line=[list(p)for p in line],rows=rows),indent=2))

