"""Reproduce R36 ray audit from archived manual observations (local P06 frame)."""
from pathlib import Path
import json,numpy as np
from camera_math import basis,project
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';old=json.loads((B/'reports/R36_facade_camera_audit.json').read_text());r=json.loads((B/'reports'/old['camera_report']).read_text());p=np.array(r['candidates']['triangular_canopy']['camera']);s=json.loads((B/'config/foundation.json').read_text())['calibration']['meters_per_canonical_pixel']
xyz=lambda q:np.array([(575-q[0])*s,(q[1]-447)*s,0.]);q=json.loads((B/'config/gallery_reveals_revised.json').read_text());a,b=map(xyz,q['facade_endpoints']);axis=(b-a)/np.linalg.norm(b-a);n=np.cross(axis,[0,0,1]);n/=np.linalg.norm(n)
def intersect(pixel):
 d=np.array([(pixel[0]-r['size'][0]/2)/np.exp(p[6]),-(pixel[1]-r['size'][1]/2)/np.exp(p[6]),1.])@basis(p);q=p[:3]+d*(np.dot(a-p[:3],n)/np.dot(d,n));return float(np.dot(q-a,axis)),float(q[2])
rows=[]
for row in old['landmarks']:
 pix=row['manual_front_head_px'];t,z=intersect(pix);bounds=[intersect(np.array(pix)+[dx,dy])[1] for dx in [-5,0,5] for dy in [-5,0,5]];got=dict(bay=row['bay'],manual_front_head_px=pix,t_m=t,z_m=z,reading_only_z_range_m=[min(bounds),max(bounds)])
 for prefix,zv in [('old',old['old_head_m']),('candidate',old['candidate_head_m'])]:got[prefix+'_head_pixel_error']=float(np.linalg.norm(project(p,[a+axis*t+[0,0,zv]],r['size'])[0]-pix))
 rows.append(got)
old['landmarks']=rows
for prefix in ['old','candidate']:old[prefix+'_rmse_px']=float(np.sqrt(np.mean([r[prefix+'_head_pixel_error']**2 for r in rows])))
(B/'reports/R36_facade_camera_audit.json').write_text(json.dumps(old,indent=2),encoding='utf8');print(old['old_rmse_px'],old['candidate_rmse_px'])
