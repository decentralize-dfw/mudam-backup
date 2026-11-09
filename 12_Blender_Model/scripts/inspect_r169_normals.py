from pathlib import Path
import bpy,json,numpy as np
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v064.blend'));o=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];p=json.loads((R/'.local_source_cache/r169/facade_planes_v062.json').read_text());q=np.array(p['q']);ns=np.array([s['normal'] for s in p['sides']]);tot=[0]*4;neg=[0]*4;top=[0,0]
for f in o.data.polygons:
 if f.center.z>-63:
  top[0]+=1;top[1]+=f.normal.z<0
 else:
  c=np.array(f.center[:2]);k=int(np.argmin([abs(ns[i]@(c-q[i])) for i in range(4)]));tot[k]+=1;neg[k]+=np.dot(ns[k],f.normal[:2])<0
print('NORMALS',tot,neg,top)
