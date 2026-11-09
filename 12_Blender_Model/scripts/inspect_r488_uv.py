import bpy,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R487_KUZEYBATI_ALT_GECIT_ADAY_v001.blend'));out={}
for name in ['R152_HISTORIC_WALL_49911001','R152_CLASS2_TERRAIN']:
 o=bpy.data.objects[name];out[name]={'uvLayers':[x.name for x in o.data.uv_layers],'materialUv':[(m.name,n.uv_map) for m in o.data.materials for n in m.node_tree.nodes if n.type=='UVMAP']}
 if name=='R152_CLASS2_TERRAIN':
  ids=list(range(0,len(o.data.loops),max(1,len(o.data.loops)//3000)));p=np.array([list(o.matrix_world@o.data.vertices[o.data.loops[i].vertex_index].co)[:2]+[1] for i in ids]);out[name]['fits']={}
  for uv in o.data.uv_layers:
   v=np.array([list(uv.data[i].uv) for i in ids]);c=np.linalg.lstsq(p,v,rcond=None)[0];out[name]['fits'][uv.name]={'coefficients':c.tolist(),'max':float(np.max(abs(p@c-v)))}
(R/'reports/R488_UV_DIAGNOSTIC.json').write_text(json.dumps(out,indent=2));print(out)
