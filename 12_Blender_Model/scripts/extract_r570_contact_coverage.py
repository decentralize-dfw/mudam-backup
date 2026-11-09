import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R569_GUNEY_SUR_TAM_DONUS_KAPALI_ADAY_v001.blend'));regions=[dict(name='SOUTH_RETURN_CONTACT',bounds=[47,-61,53,-51],triangles=[]),dict(name='EAST_RETURN_CONTACT',bounds=[70,-61,89,-37],triangles=[])]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or o.name.startswith('R158_TREE_'):continue
 bb=[o.matrix_world@Vector(v)for v in o.bound_box];targets=[q for q in regions if not(max(v.x for v in bb)<q['bounds'][0]or min(v.x for v in bb)>q['bounds'][2]or max(v.y for v in bb)<q['bounds'][1]or min(v.y for v in bb)>q['bounds'][3])]
 if not targets:continue
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  for q in targets:
   a,b,c,d=q['bounds']
   if max(v.x for v in p)<a or min(v.x for v in p)>c or max(v.y for v in p)<b or min(v.y for v in p)>d:continue
   q['triangles'].append([[v.x,v.y]for v in p])
(R/'reports/R570_REGION_COVERAGE.json').write_text(json.dumps(regions));print([(q['name'],len(q['triangles']))for q in regions])

