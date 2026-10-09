from pathlib import Path
import bpy,json,math
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R113_build_report.json').read_text());t=json.loads((B/'reports/R05_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
c=Vector(t['center_world']);ex=Vector(t['canonical_x_world']);ey=Vector(t['canonical_y_world']);up=Vector((0,0,1));a=t['top_angle_inner'];b=t['top_angle_outer'];pi=c+(ex*math.cos(a)+ey*math.sin(a))*t['inner_radius'];po=c+(ex*math.cos(b)+ey*math.sin(b))*t['outer_radius'];rows=[];dep=bpy.context.evaluated_depsgraph_get()
for f in [0,.25,.5,.75,1]:
 p=pi.lerp(po,f)+up*(t['lower_z']+.1);h=bpy.context.scene.ray_cast(dep,p,up,distance=8);rows.append(dict(fraction=f,point=list(p),hit=h[4].name if h[0] else None,z=h[1].z if h[0] else None))
q=dict(file=r['file'],inner_top=list(pi),outer_top=list(po),under_top_rays=rows);(B/'reports/R113_lower_stair_pier_inspection.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))
