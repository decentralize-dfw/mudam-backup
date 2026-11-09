from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/station_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for x in [-318,-313,-308,-300,-290,-280,-270,-265]:
 for y in [210,220,230,240,250,260,265]:
  hit,h,n,*_=bpy.context.scene.ray_cast(dg,Vector((x,y,50)),Vector((0,0,-1)),distance=150)
  if hit:rows.append([x,y,round(h.z,3),round(n.z,3)])
(R/'reports/R178_ground_samples.json').write_text(json.dumps(rows));print(rows)
