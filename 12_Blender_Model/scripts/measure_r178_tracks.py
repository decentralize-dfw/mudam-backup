from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/station_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for row in json.loads((R/'config/r178_funicular_tracks.json').read_text()):
 a,b=[Vector(p) for p in row['xy']];sample=[]
 for t in [.4,.5,.6,.7,.8]:
  p=a.lerp(b,t)
  if p.x>-314:continue
  hit,h,n,*_=bpy.context.scene.ray_cast(dg,Vector((*p,50)),Vector((0,0,-1)),distance=150)
  if hit:sample.append([*p,h.z])
 if sample:rows.append({'id':row['id'],'samples':sample})
(R/'reports/R178_TRACK_SOURCE.json').write_text(json.dumps(rows,indent=2));print(rows)
