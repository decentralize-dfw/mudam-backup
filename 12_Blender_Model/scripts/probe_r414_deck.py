import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R413_KALE_KULE_UCU_ORTU_ADAY_v001.blend'));dg=bpy.context.evaluated_depsgraph_get();out=[]
for px,py in [(662,270),(649,350),(830,468),(285,747),(700,400)]:
 x=-74.5+px*65/1100;y=-1.5-py*65/1100;hits=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or not o.name.startswith(('R154_FORT','R389','R400','R401')):continue
  ev=o.evaluated_get(dg);inv=o.matrix_world.inverted();hit,loc,no,fi=ev.ray_cast(inv@Vector((x,y,20)),inv.to_3x3()@Vector((0,0,-1)))
  if hit:hits.append((o.name,(o.matrix_world@loc).z))
 out.append(dict(pixel=[px,py],hits=sorted(hits,key=lambda h:-h[1])))
(R/'reports/R414_DECK_VISIBILITY.json').write_text(json.dumps(out,indent=2));print(out)
