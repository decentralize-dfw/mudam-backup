from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R146_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));q=json.loads((B/'reports/R146_render_receipt.json').read_text())['images'][1];eye=Vector(q['eye']);target=Vector(q['target']);quat=(target-eye).to_track_quat('-Z','Y');cam=bpy.data.cameras.new('probe');cam.lens=24;S=bpy.context.scene;S.render.resolution_x=1200;S.render.resolution_y=1000;S.render.resolution_percentage=100;corners=cam.view_frame(scene=S);dep=bpy.context.evaluated_depsgraph_get()
for x,y in [(.25,.55),(.5,.55),(.75,.55),(.5,.7)]:
 # corners: top-right, bottom-right, bottom-left, top-left
 local=(corners[3]*(1-x)+corners[0]*x)*(1-y)+(corners[2]*(1-x)+corners[1]*x)*y;direction=(quat@local).normalized();origin=eye.copy()
 for i in range(80):
  hit,p,n,fi,o,m=S.ray_cast(dep,origin,direction)
  if not hit:break
  if not o.hide_render and o.visible_get():print('HIT',x,y,o.name,fi,list(p));break
  origin=p+direction*.001
