import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R392_KALE_BAGIMSIZ_TOPRAK_ORTU_ADAY_v001.blend'));eye=Vector((90,-105,55));direction=(Vector((28,-36,-3))-eye).normalized();rot=direction.to_track_quat('-Z','Y');right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));deps=bpy.context.evaluated_depsgraph_get();rows=[]
for px,py in [(590,441),(600,445),(620,452),(660,470),(704,487),(177,371),(190,365),(595,437),(600,451),(680,480),(650,473)]:
 origin=eye+right*((px/1000-.5)*75)+up*((.5-py/850)*63.75);hit,loc,n,idx,ob,mat=bpy.context.scene.ray_cast(deps,origin,direction,distance=1000);rows.append(dict(pixel=[px,py],hit=hit,name=ob.name if hit else None,xyz=list(loc) if hit else None,face=idx))
(R/'reports/R395_PAVILION_JUNCTION_RAYS.json').write_text(json.dumps(rows,indent=2));print(rows)
