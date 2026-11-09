from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R209_NOVOTEL_CATILAR_v001.blend'));s=bpy.context.scene;out=[]
for px,py in [(529,687),(652,704),(675,943),(869,985),(127,779),(500,700),(850,1000)]:
 origin=Vector((255+px*.1125,525-py*.1125,200));hits=[]
 for k in range(5):
  hit,p,n,ix,o,mat=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,Vector((0,0,-1)))
  if not hit:break
  poly=o.data.polygons[ix] if ix<len(o.data.polygons) else None
  hits.append(dict(object=o.name,point=list(p),face=ix,normal=list(n),material=o.data.materials[poly.material_index].name if poly and poly.material_index<len(o.data.materials) else None,hidden=o.hide_render))
  origin=p-Vector((0,0,.005))
 out.append(dict(pixel=[px,py],hits=hits))
(R/'reports/R210_GROUND_PICKS.json').write_text(json.dumps(out,indent=2));print(out)
