from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));d=bpy.context.evaluated_depsgraph_get();samples=[]
for x in range(0,200,5):
 for y in range(390,480,5):
  hit,p,n,*_=bpy.context.scene.ray_cast(d,Vector((x,y,100)),Vector((0,0,-1)),distance=200)
  if hit and n.z>.95 and p.z<25:samples.append([x,y,p.z])
(R/'reports/R176_PIAZZA_SAMPLES.json').write_text(json.dumps(samples));print(np.quantile(np.array(samples)[:,2],[0,.1,.5,.9,1]))
