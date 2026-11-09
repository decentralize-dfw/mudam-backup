import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];out={}
for ver in ['MUDAM_R324_MUZE_TERAS_TEMAS_ADAY_v001','MUDAM_R326_KUZEY_KALINTI_PLAN_ADAY_v001']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/(ver+'.blend')));rows=[]
 for n in ['R158_TREE_05911','R158_TREE_05753','R158_TREE_05356','R158_TREE_06116']:
  o=bpy.data.objects[n];rows.append(dict(name=n,matrix=[list(x) for x in o.matrix_world],location=list(o.location),scale=list(o.scale),vertices=len(o.data.vertices),firstVertex=list(o.data.vertices[0].co),hideRender=o.hide_render,hideViewport=o.hide_viewport))
 out[ver]=rows
(R/'reports/R326_TREE_VISIBILITY_CHECK.json').write_text(json.dumps(out,indent=2));print(out)
