"""Opposite-side 116 test of entrance canopy outline; no image or plan deformation."""
from pathlib import Path
import numpy as np,json,math
from PIL import Image,ImageDraw,ImageFont
from camera_math import solve,basis,project
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
F=json.loads((B/'config/foundation.json').read_text());D=json.loads((B/'config/vertical_study.json').read_text());Q=json.loads((B/'config/roof_revision.json').read_text())
s=F['calibration']['meters_per_canonical_pixel'];z=lambda y:(436-y)*D['section_m_per_px']
def xyz(p,h):return [(575-p[0])*s,(p[1]-447)*s,h]
names=['A_east_back_roof_corner','B_east_front_roof_corner','C_canopy_tip','D_west_front_roof_corner','E_main_apex','F_pavilion_apex','G_cap_left','H_cap_right','I_high_roof_left','J_high_roof_front']
pixels=np.array([[670,667],[730,718],[1570,776],[1583,658],[1156,447],[380,657],[1122,476],[1190,476],[1003,633],[1221,639]])
common=[xyz([289.5,347.3],z(287)),xyz([289.5,534.7],z(287)),xyz([575,816],z(287)),xyz([862.5,534.7],z(287)),xyz([575,447],Q['apex_z']),xyz([107,279],z(280)),xyz(Q['inner_canonical'][6],Q['lantern_top_z']),xyz(Q['inner_canonical'][3],Q['lantern_top_z']),xyz(Q['outer_canonical'][6],Q['eave_z'][6]),xyz(Q['outer_canonical'][5],Q['eave_z'][5])]
source=next((R/'05_Dis_Mekan').rglob('116_*'));size=list(Image.open(source).size)
train=np.array([i<6 for i in range(len(common))]);results={}
starts=[]
for dist in [80,150,260]:
 for angle in [.25,.6,1.0]:
  for height in [20,40]:starts.append([dist*np.sin(angle),dist*np.cos(angle),height,math.pi+angle,-.05,0,np.log(dist*15)])
bounds=([0,25,5,math.pi,-.6,-.15,np.log(300)],[700,900,150,math.pi+1.5,.4,.15,np.log(25000)])
for key in ['triangular_canopy','old_recessed_outline']:
 pts=np.array(common)
 if key=='old_recessed_outline':pts[2]=xyz([674.7,721.6],z(287))
 p,runs=solve(pts[train],pixels[train],size,starts,bounds);pred=project(p,pts,size);err=np.linalg.norm(pred-pixels,axis=1)
 results[key]=dict(camera=p.tolist(),basis_rows=basis(p).tolist(),focal_px=float(np.exp(p[6])),fit_rmse_px=float(np.sqrt(np.mean(err[train]**2))),holdout_rmse_px=float(np.sqrt(np.mean(err[~train]**2))),landmarks=[dict(id=n,local_xyz=pts[i].tolist(),photo_px=pixels[i].tolist(),predicted_px=pred[i].tolist(),error_px=float(err[i]),role='fit' if train[i] else 'holdout') for i,n in enumerate(names)],runs=runs)
 im=Image.open(source).convert('RGB');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
 for i,(u,v) in enumerate(pixels):
  x,y=pred[i];color='#55ffb6' if train[i] else '#ffd966';dr.ellipse((u-6,v-6,u+6,v+6),outline=color,width=2);dr.line((u,v,x,y),fill='#ff405e',width=2);dr.line((x-5,y-5,x+5,y+5),fill='#ff405e',width=2);dr.line((x-5,y+5,x+5,y-5),fill='#ff405e',width=2);dr.text((u+10,v-22),names[i][0],fill=color,font=font)
 dr.rectangle((20,20,1750,115),fill='#10191d');dr.text((35,30),'116 / '+key,font=font,fill='white');dr.text((35,65),f"fit {results[key]['fit_rmse_px']:.2f}px / held-out roof {results[key]['holdout_rmse_px']:.2f}px / CONDITIONAL",font=font,fill='#ffd966');im.save(B/f'renders/qa/P06_116_{key}.png')
report=dict(source_path=source.relative_to(R).as_posix(),size=size,status='conditional_not_metric_pose',method='Six manually identified building/pavilion points fit camera. Four main roof points withheld. Source 102 canopy outline and 008/011/116 support topology.',limits=['Roof corner identities are manually interpreted; approx 5 px reading uncertainty plus source error.','Comparison alone cannot validate all heights or precise camera.','Main roof holdouts also depend on conditional section heights.'],candidates=results)
(B/'reports/P06_camera_fit_116.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:{n:v[n] for n in ['fit_rmse_px','holdout_rmse_px','camera']} for k,v in results.items()},indent=2))
