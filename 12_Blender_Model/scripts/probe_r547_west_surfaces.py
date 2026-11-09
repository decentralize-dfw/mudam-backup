import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];results={}
for tag,path in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('candidate','scenes/MUDAM_R546_BATI_HENDEK_KENAR_BUTUNLUGU_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));dg=bpy.context.evaluated_depsgraph_get();rows=[]
 for x,y in [(-20.5,10.5),(-17,10),(-15,9),(-23,10.5),(-25,10),(-26,1.5),(-26,2),(-26,3),(-25,3),(-24,2),(-27,2),(-32,2.8)]:
  h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1)),distance=80);rows.append(dict(x=x,y=y,z=p.z if h else None,object=o.name if h else None,material=o.data.materials[o.data.polygons[f].material_index].name if h and f<len(o.data.polygons) and o.data.materials else None))
 results[tag]=rows
(R/'reports/R547_WEST_SURFACE_PROBES.json').write_text(json.dumps(results,indent=2));print(results)
