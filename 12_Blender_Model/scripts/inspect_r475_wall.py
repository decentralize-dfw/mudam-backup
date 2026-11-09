import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out={}
pts=[(250,950),(350,880),(450,810),(550,740),(650,670),(750,600),(850,530),(930,470)]
for key,path in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('model','scenes/MUDAM_R464_AVLU_CAMI_ZEMIN_KESISI_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rows=[]
 for px,py in pts:
  x,y=-65.5+px*.035,54.5-py*.035;hit,loc,n,idx,ob,ma=s.ray_cast(dg,Vector((x,y,50)),Vector((0,0,-1)),distance=100);rows.append(dict(px=px,py=py,x=x,y=y,z=loc.z if hit else None,obj=ob.name if hit else None))
 out[key]=rows
(R/'reports/R475_DIAGONAL_WALL_RAYS.json').write_text(json.dumps(out,indent=2));print(out)
