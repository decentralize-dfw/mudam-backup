"""Compare fixed P06 geometry with two independent rear-view photographs."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from camera_math import solve,project,basis
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
F=json.loads((B/'config/foundation.json').read_text());D=json.loads((B/'config/vertical_study.json').read_text());Q=json.loads((B/'config/roof_revision.json').read_text())
s=F['calibration']['meters_per_canonical_pixel'];z=lambda y:(436-y)*D['section_m_per_px']
def xyz(p,h):return [(575-p[0])*s,(p[1]-447)*s,h]
o=Q['outer_canonical'];inn=Q['inner_canonical'];a=Q['eave_z'];b=Q['shoulder_z'];cap=Q['lantern_top_z'];apex=Q['apex_z']
names=['A_apex','B_cap_left','C_cap_right','D_high_eave_left','E_high_eave_right','F_low_eave_left','G_low_eave_right','H_high_shoulder_left','I_high_shoulder_right','J_low_shoulder_left','K_low_shoulder_right','L_west_wall_tip','M_east_wall_tip']
points=np.array([xyz([575,447],apex),xyz(inn[2],cap),xyz(inn[7],cap),xyz(o[3],a[3]),xyz(o[6],a[6]),xyz(o[2],a[2]),xyz(o[7],a[7]),xyz(inn[3],b[3]),xyz(inn[6],b[6]),xyz(inn[2],b[2]),xyz(inn[7],b[7]),xyz([862.5,262.6],z(287)),xyz([289.5,266.5],z(287))])
obs={'119':[[803,365],[776,385],[830,385],[630,552],[980,552],[623,600],[987,600],[777,447],[831,447],[777,493],[831,493],[181,559],[1424,554]],
 '087':[[965,242],[935,267],[997,267],[762,465],[1168,465],[756,518],[1176,518],[935,346],[997,346],[935,394],[997,394],[254,473],[1674,469]]}
train=np.array([i<7 or i>=11 for i in range(13)]);out={}
for key,pixels in obs.items():
 source=next((R/'05_Dis_Mekan').rglob(key+'_*'));im=Image.open(source).convert('RGB');size=list(im.size);uv=np.array(pixels)
 starts=[[0,-d,h,0,.06,0,np.log(d*size[0]/120)] for d in [55,90,160,300] for h in [2,15,35]]
 bounds=([-500,-2000,-20,-.6,-.7,-.2,np.log(200)],[500,-30,100,.6,.7,.2,np.log(40000)])
 p,runs=solve(points[train],uv[train],size,starts,bounds);pred=project(p,points,size);err=np.linalg.norm(pred-uv,axis=1)
 out[key]=dict(source_path=source.relative_to(R).as_posix(),size=size,camera=p.tolist(),basis_rows=basis(p).tolist(),focal_px=float(np.exp(p[6])),fit_rmse_px=float(np.sqrt(np.mean(err[train]**2))),holdout_rmse_px=float(np.sqrt(np.mean(err[~train]**2))),landmarks=[dict(id=n,local_xyz=points[i].tolist(),photo_px=pixels[i],predicted_px=pred[i].tolist(),error_px=float(err[i]),role='fit' if train[i] else 'holdout') for i,n in enumerate(names)],runs=runs)
 dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
 for i,(u,v) in enumerate(uv):
  x,y=pred[i];color='#55ffb6' if train[i] else '#ffd966';dr.ellipse((u-5,v-5,u+5,v+5),outline=color,width=2);dr.line((u,v,x,y),fill='#ff405e',width=2);dr.line((x-5,y-5,x+5,y+5),fill='#ff405e',width=2);dr.line((x-5,y+5,x+5,y-5),fill='#ff405e',width=2);dr.text((u+8,v-18),names[i][0],fill=color,font=font)
 dr.rectangle((20,20,min(size[0]-20,1500),115),fill='#10191d');dr.text((35,30),f'{key}: roof + wing camera fit / fixed P06 geometry',font=font,fill='white');dr.text((35,65),f"fit {out[key]['fit_rmse_px']:.2f}px / withheld shoulders {out[key]['holdout_rmse_px']:.2f}px / CONDITIONAL",font=font,fill='#ffd966');im.save(B/f'renders/qa/P06_{key}_multiview.png')
report=dict(status='diagnostic_not_accepted',geometry='roof_revision.json fixed; no geometry optimization',correspondence_note='Retained P05 hall-end high wall candidate. Alternative gallery corner mapping is saved in P06_alternate_wall_corner_fit.json; wall cap thickness and endpoint identity remain unresolved.',fit_landmarks=9,withheld_landmarks=4,limits=['Both views face the same facade; opposite view 116 remains to be fit.','Wing tips now participate in fit and are NOT independent checks.','Fixed image-centre principal point; unknown crop and lens distortion.','No metric pose is accepted.'],photos=out)
(B/'reports/P06_multiview.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:{n:v[n] for n in ['fit_rmse_px','holdout_rmse_px','camera']} for k,v in out.items()},indent=2))
