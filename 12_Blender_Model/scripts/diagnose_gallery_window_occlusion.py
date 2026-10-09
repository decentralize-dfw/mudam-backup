from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';receipt=json.loads((B/'reports/R52_render_receipt.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/receipt['file']));S=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get();rows=[]
for view in receipt['images']:
 eye=Vector(view['eye']);target=Vector(view['target']);rot=(target-eye).to_track_quat('-Z','Y');lens=22 if 'two' in view['image'] else 23
 for x,y in [(600,500),(900,500),(1000,600),(800,500),(500,400)]:
  direction=rot@Vector(((x/1600-.5)*36,(.5-y/1100)*36*1100/1600,-lens)).normalized();hits=[]
  for ob in S.objects:
   if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
   eo=ob.evaluated_get(dep);inv=eo.matrix_world.inverted();hit,loc,_,_=eo.ray_cast(inv@eye,inv.to_3x3()@direction,distance=30)
   if hit:hits.append(((eo.matrix_world@loc-eye).length,ob.name,list(eo.matrix_world@loc)))
  rows.append(dict(image=view['image'],pixel=[x,y],hits=sorted(hits)[:6]))
(B/'reports/R52_occlusion_diagnosis.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
