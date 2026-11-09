from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R206_NOVOTEL_BUTUN_CATILAR_v001.blend'));s=bpy.context.scene;cam=s.camera;rot=cam.matrix_world.to_quaternion();right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));dire=rot@Vector((0,0,-1));out=[]
for px,py in [(464,562),(524,624),(346,390),(437,565),(481,619)]:
 origin=cam.matrix_world.translation+right*((px/1400-.5)*170)+up*((.5-py/1000)*170*1000/1400);h,p,n,ix,o,mat=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,dire)
 out.append(dict(pixel=[px,py],hit=h,object=o.name if h else None,point=list(p) if h else None,face=ix))
(R/'reports/R208_WHITE_SEAM_PICKS.json').write_text(json.dumps(out,indent=2));print(out)
