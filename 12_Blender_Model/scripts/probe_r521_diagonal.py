import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];rows=[]
for label,path in [('source','.local_source_cache/r316/museum_ring_reference.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));dg=bpy.context.evaluated_depsgraph_get()
 for px,py in [(270,550),(300,520),(350,480),(400,440),(450,400),(490,360),(450,350),(400,390),(350,430),(300,470),(350,540),(400,500),(450,460),(500,420)]:
  x=-24+px*26/800;y=8-py*26/800;h,p,n,i,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,50)),Vector((0,0,-1)),distance=100);rows.append(dict(label=label,pixel=[px,py],xy=[x,y],hit=o.name if h else None,z=p.z if h else None))
(R/'reports/R521_DIAGONAL_APPROACH_PROBES.json').write_text(json.dumps(rows,indent=2));print(rows)

