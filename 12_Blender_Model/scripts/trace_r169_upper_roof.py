from pathlib import Path
import json,numpy as np
R=Path('12_Blender_Model');D=R/'.local_source_cache/r169';a=np.load(D/'164179154.npz');angle=float(a['angle']);rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]);pixels=[[155,481],[1117,266],[1208,701],[213,910],[470,641],[907,520]];v=[]
for px,py in pixels:
 xy=np.array([38+(px-700)*29/1400,-273+(550-py)*29/1400]);local=xy@rot;i=int(np.argmin(abs(a['x']-local[0])));j=int(np.argmin(abs(a['y']-local[1])));patch=a['z'][max(0,j-1):j+2,max(0,i-1):i+2];z=float(np.nanmedian(patch));v.append([*xy,z])
faces=[[0,4,5,1],[1,5,2],[2,5,4,3],[3,4,0]]
# Shared ridge corners remain source sampled; quad planarization is inspected, not assumed.
(D/'upper_roof_trace_33.json').write_text(json.dumps(dict(vertices=v,faces=faces,source_pixels=pixels,source_image='R169_33_roof_source.png',pixel_scale_m=29/1400,limits='Manual source tracing, 0.4m roof sample median; not survey. Dormers and chimney remain separate.'),indent=2));print(v)
