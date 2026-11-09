from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_CEPHE_GEOMETRI_ADAY_v006.blend'))
o=bpy.data.objects['R169_MEASURED_ENVELOPE'];data=json.loads((D/'roof_planes_33.json').read_text());import numpy as np
p=np.array(data['points']);a=np.load(D/'164179154.npz');ang=float(a['angle']);rot=np.array([[np.cos(ang),-np.sin(ang)],[np.sin(ang),np.cos(ang)]])
labels=np.full(len(p),-1)
for i,plane in enumerate(data['planes']):labels[plane['indices']]=i
changed=[];roofverts=set()
for f in o.data.polygons:
 if f.normal.z>.25:roofverts.update(f.vertices)
for i in roofverts:
 v=o.data.vertices[i];local=np.array([v.co.x,v.co.y])@rot;dist=np.sum((p[:,:2]-local)**2,axis=1);j=int(dist.argmin());label=int(labels[j])
 if dist[j]>.18 or label<0:continue
 c=data['planes'][label]['coeff'];z=c[0]*local[0]+c[1]*local[1]+c[2];dz=z-v.co.z
 if abs(dz)>.18:continue
 v.co.z=z;changed.append(float(dz))
o.data.update();out=R/'scenes/MUDAM_R169_CEPHE_CATI_ADAY_v007.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
(R/'reports/R169_ROOF_PLANES_v007.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changed_roof_vertices=len(changed),max_change_m=max(map(abs,changed)),roof_plane_sample_rmse_m=[p['rmse'] for p in data['planes']],reopened=True,scope='Supported roof vertices constrained to locally sampled planes; unmatched dormer and edge points retained. Six front openings retained. Not full building acceptance.'),indent=2));print('ROOF_PLANES_APPLIED',len(changed))
