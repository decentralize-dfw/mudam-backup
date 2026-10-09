from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');r=json.loads((B/'reports/R23_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));deps=bpy.context.evaluated_depsgraph_get();out=[]
for ob in bpy.data.objects:
 if ob.name.startswith('P05_CLERESTORY'):
  row={'name':ob.name,'visible':ob.visible_get(),'hide_render':ob.hide_render,'mats':[]}
  for m in ob.data.materials:
   bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None;row['mats'].append({'name':m.name,'use_nodes':m.use_nodes,'rgba':list(m.diffuse_color),'transmission':bs.inputs['Transmission Weight'].default_value if bs else None})
  center=sum((ob.matrix_world@v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices);row['center']=list(center);out.append(row)
print(json.dumps(out,indent=2))
