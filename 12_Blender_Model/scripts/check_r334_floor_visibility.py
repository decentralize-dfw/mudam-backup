import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R334_HENDEK_CAKISMA_TEMIZLIK_ADAY_v001.blend'))
data=json.loads((R/'reports/R331_OUTER_MOAT_PLANES.json').read_text());rows=[]
dg=bpy.context.evaluated_depsgraph_get()
for name,row in data.items():
 if not row.get('valid'):continue
 xy=row['outline'];a,b,c=row['plane']
 for t in [.2,.5,.8]:
  l=Vector(xy[0]).lerp(Vector(xy[3]),t);r=Vector(xy[1]).lerp(Vector(xy[2]),t)
  for u in [.2,.5,.8]:
   q=l.lerp(r,u);hit,loc,n,idx,ob,mat=bpy.context.scene.ray_cast(dg,Vector((q.x,q.y,15)),Vector((0,0,-1)),distance=30)
   rows.append(dict(region=name,xy=list(q),expected=a*q.x+b*q.y+c,hit=ob.name if ob else None,z=loc.z if hit else None))
(R/'reports/R334_FLOOR_VISIBILITY.json').write_text(json.dumps(rows,indent=2));print(rows)
