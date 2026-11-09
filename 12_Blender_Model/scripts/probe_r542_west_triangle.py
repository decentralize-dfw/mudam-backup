import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];results={}
for tag,path in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('candidate','scenes/MUDAM_R540_KUZEY_KALINTI_SUR_HENDEK_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));dg=bpy.context.evaluated_depsgraph_get();rows=[]
 for x,y in [(-29,3),(-28,3),(-30,4),(-26,2),(-25,2),(-24,2),(-31,4),(-32,4),(-29,2)]:
  h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1)),distance=80);rows.append(dict(x=x,y=y,z=p.z if h else None,object=o.name if h else None,material=o.data.materials[o.data.polygons[f].material_index].name if h and f<len(o.data.polygons) and o.data.materials else None))
 results[tag]=rows
(R/'reports/R542_WEST_TRIANGLE_PROBES.json').write_text(json.dumps(results,indent=2));print(results)
