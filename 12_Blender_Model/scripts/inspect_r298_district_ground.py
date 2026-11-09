import bpy,json,re
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R297_DOGU_GUNEY_CATI_MALZEME_ADAY_v001.blend'))
targets=['R182_DISTRICT_164184549','R182_DISTRICT_930614764','R171_546345955'];rows=[]
for name in targets:
 ob=bpy.data.objects[name];pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=Vector(tuple(min(p[i] for p in pts)-2 for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts)+2 for i in range(3)));near=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.name==name or o.hide_render:continue
  if any(k in o.name for k in ['TREE','LEAF','TRUNK','FOLIAGE']):continue
  corners=[o.matrix_world@Vector(v) for v in o.bound_box]
  if all(max(p[i] for p in corners)>=lo[i] and min(p[i] for p in corners)<=hi[i] for i in range(3)):
   near.append(dict(name=o.name,vertices=len(o.data.vertices),z=[min(p.z for p in corners),max(p.z for p in corners)]))
 rows.append(dict(name=name,bounds=[list(lo),list(hi)],near=near))
(R/'reports/R298_DISTRICT_NEIGHBORS.json').write_text(json.dumps(rows,indent=2));print(rows,flush=True)
