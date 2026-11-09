import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');samples=[(175,270),(230,270),(260,300),(200,300),(250,350),(280,400),(320,440),(350,500),(400,540),(440,580),(480,530),(530,580),(570,630),(450,650),(380,570),(350,450),(370,380),(300,240),(350,200),(410,140),(430,80),(380,130),(270,180),(290,260),(210,400),(250,450),(300,520),(400,610),(550,690),(600,720),(450,750),(500,800),(700,750)]
out={}
for label,scene in [('current',R/'scenes/MUDAM_R585_DOGU_HENDEK_CIFT_ZEMIN_TEMIZ_ADAY_v001.blend'),('source',R/'.local_source_cache/r316/museum_ring_reference.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(scene));dg=bpy.context.evaluated_depsgraph_get();rows=[]
 for u,v in samples:
  x=-59+u*.038;y=27-v*.038;h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1)),distance=80);rows.append(dict(pixel=[u,v],xy=[x,y],z=p.z if h else None,obj=o.name if h else None))
 out[label]=rows
(R/'reports/R586_WEST_LEVELS.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
