"""Fixed-geometry, conditional photograph camera fit. Requires NumPy and Pillow.
No source image warping and no geometry parameters are optimized.
"""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[2]; B=R/'12_Blender_Model'
D=json.loads((B/'config/vertical_study.json').read_text())
F=json.loads((B/'config/foundation.json').read_text())
s=F['calibration']['meters_per_canonical_pixel']; z=lambda y:(436-y)*D['section_m_per_px']
# Section readings remain conditional: section trace and original date unresolved.
outer=[[558,334],[592,334],[688,430],[688,464],[592,560],[558,560],[462,464],[462,430]]
inner=[[558,427],[592,427],[595,430],[595,464],[592,467],[558,467],[555,464],[555,430]]
# Low and high halves have separate eaves/shoulders. Corner strips bridge them.
base=[z(287)]*3+[z(247)]*4+[z(287)]
shoulder=[z(210)]*3+[z(170)]*4+[z(210)]
cap=z(131); apex=z(111)
cfg=dict(version=1,status='conditional_topology_study_not_accepted',sources=['102','101','119','116','026'],
 outer_canonical=outer,inner_canonical=inner,eave_z=base,shoulder_z=shoulder,lantern_top_z=cap,apex_z=apex,
 section_picks={'low_eave_y':287,'high_eave_y':247,'low_shoulder_y':210,'high_shoulder_y':170,'lantern_top_y':131,'apex_y':111},
 assumptions=['102 floor silhouette constrains outer extent; roof edge is not independently surveyed.',
 '34 canonical pixel corner strip is a visual hypothesis, not a plan dimension.',
 'Inner footprint is a chamfered square candidate with 40 canonical pixel total width.',
 'High half assigned toward entrance from photo 116; low half faces photo 119.',
 'No roof skin thickness, structural profile or panel grid inferred.'])
(B/'config/roof_revision.json').write_text(json.dumps(cfg,indent=2),encoding='utf8')

def xyz(p,h):return [(575-p[0])*s,(p[1]-447)*s,h]
# The same visible semantic landmarks are used for both candidates.
observations=[
 ('A_apex',[803,365],'fit'),('B_cap_left',[776,385],'fit'),('C_cap_right',[830,385],'fit'),
 ('D_high_eave_left',[630,552],'fit'),('E_high_eave_right',[980,552],'fit'),
 ('F_low_eave_left',[623,600],'fit'),('G_low_eave_right',[987,600],'fit'),
 ('H_high_shoulder_left',[777,447],'holdout'),('I_high_shoulder_right',[831,447],'holdout'),
 ('J_low_shoulder_left',[777,493],'holdout'),('K_low_shoulder_right',[831,493],'holdout')]
def landmarks(o,inn,bs,sh,cz,az):
 return np.array([xyz([575,447],az),xyz(inn[2],cz),xyz(inn[7],cz),
  xyz(o[3],bs[3]),xyz(o[6],bs[6]),xyz(o[2],bs[2]),xyz(o[7],bs[7]),
  xyz(inn[3],sh[3]),xyz(inn[6],sh[6]),xyz(inn[2],sh[2]),xyz(inn[7],sh[7])])
new=landmarks(outer,inner,base,shoulder,cap,apex)
old_o=np.array([[565,334],[585,334],[688,437],[688,457],[585,560],[565,560],[462,457],[462,437]])
old_i=(old_o-[575,447])*.18+[575,447]
old=landmarks(old_o,old_i,[z(287)]*8,[z(170)]*8,cap,apex)
uv=np.array([o[1] for o in observations]); train=np.array([o[2]=='fit' for o in observations])

def basis(p):
 yaw,pitch,roll=p[3:6]; sy,cy=np.sin(yaw),np.cos(yaw)
 forward=np.array([sy*np.cos(pitch),cy*np.cos(pitch),np.sin(pitch)])
 right=np.array([cy,-sy,0]); up=np.cross(right,forward)
 return np.array([right*np.cos(roll)+up*np.sin(roll),up*np.cos(roll)-right*np.sin(roll),forward])
def project(p,pts):
 q=(pts-p[:3])@basis(p).T
 return np.array([800,377])+np.exp(p[6])*q[:,:2]/q[:,2,None]*[1,-1]
def fit(pts):
 def residual(p):
  # No priors are included in reported image errors. Reject impossible starts separately.
  return (project(p,pts)[train]-uv[train]).ravel()
 best=None
 for dist in [80,160,320]:
  for height in [2,15,30]:
   p=np.array([0.,-dist,float(height),0.,.03,0.,np.log(dist*13.4)]); damping=1e-2
   for it in range(180):
    r=residual(p); eps=np.array([1e-3]*3+[1e-6]*4)
    jac=np.column_stack([(residual(p+np.eye(7)[i]*eps[i])-r)/eps[i] for i in range(7)])
    a=jac.T@jac; delta=np.linalg.solve(a+damping*np.diag(np.maximum(np.diag(a),1e-8)),-jac.T@r)
    q=p+delta
    valid=-2000<q[1]<-35 and -20<q[2]<100 and abs(q[0])<500 and abs(q[3])<.7 and abs(q[4])<.7 and abs(q[5])<.2 and 200<np.exp(q[6])<40000
    if valid and np.linalg.norm(residual(q))<np.linalg.norm(r):
     p=q;damping=max(damping/3,1e-10)
     if np.linalg.norm(delta)<1e-8:break
    else:damping=min(damping*5,1e12)
   cost=np.linalg.norm(residual(p))
   if best is None or cost<best[0]:best=(cost,p)
 return best[1]

results={}
for name,pts in [('legacy',old),('revised',new)]:
 p=fit(pts); pred=project(p,pts);err=np.linalg.norm(pred-uv,axis=1)
 results[name]=dict(camera_parameters=p.tolist(),camera_basis_rows=basis(p).tolist(),focal_px=float(np.exp(p[6])),
  fit_rmse_px=float(np.sqrt(np.mean(err[train]**2))),holdout_rmse_px=float(np.sqrt(np.mean(err[~train]**2))),
  points=[dict(id=o[0],observed_px=o[1],role=o[2],model_local_xyz=pts[i].tolist(),projected_px=pred[i].tolist(),error_px=float(err[i])) for i,o in enumerate(observations)])

source=next((R/'05_Dis_Mekan').rglob('119_*'))
report=dict(source_photo='119',source_path=source.relative_to(R).as_posix(),image_size=[1600,754],principal_point_px=[800,377],
 camera_status='conditional_diagnostic_not_metric_pose',landmark_selection='Manual pixel picks, approximately 3 px reading tolerance; correspondence uncertainty additional.',
 method='Fixed geometry, 7 camera parameters, perspective pinhole, NumPy damped least squares, 9 starts. Geometry unchanged by optimization.',
 limits=['Unknown crop/intrinsics/lens distortion; principal point fixed to image centre.',
 '4 holdouts are withheld shoulder landmarks on the SAME photograph, not independent photographs.',
 'Absolute scale inherited from OSM/section; image fitting does not validate metres.',
 'Outer silhouette points partly occlude each other; correspondence is a hypothesis.',
 'A low residual does not prove unique camera or complete building accuracy.'],candidates=results)
wing_pts=np.array([xyz([862.5,262.6],z(287)),xyz([289.5,266.5],z(287))])
wing_uv=np.array([[181,559],[1424,554]])
wing_pred=project(np.array(results['revised']['camera_parameters']),wing_pts)
report['cross_system_checks']=[dict(id=n,role='not_used_in_camera_fit',observed_px=wing_uv[i].tolist(),projected_px=wing_pred[i].tolist(),error_px=float(np.linalg.norm(wing_pred[i]-wing_uv[i])),correspondence='Candidate outer high stone wall tip; height/location correspondence still unresolved') for i,n in enumerate(['west_high_wall_tip','east_high_wall_tip'])]
report['acceptance']='NOT_ACCEPTED: wing checks disagree; camera and whole shell remain conditional.'
report['legacy_fit_limitation']='Best legacy fit hits the 35 m minimum distance search bound; comparison is diagnostic, not an unconstrained global optimum claim.'
(B/'reports/P06_camera_fit_119.json').write_text(json.dumps(report,indent=2),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for name,res in results.items():
 im=Image.open(source).convert('RGB');dr=ImageDraw.Draw(im)
 for v in res['points']:
  u,w=v['observed_px'];a,b=v['projected_px'];c='#55ffb6' if v['role']=='fit' else '#ffd966'
  dr.ellipse((u-5,w-5,u+5,w+5),outline=c,width=2);dr.line((u,w,a,b),fill='#ff6070',width=2)
  dr.line((a-5,b-5,a+5,b+5),fill='#ff6070',width=2);dr.line((a-5,b+5,a+5,b-5),fill='#ff6070',width=2)
  dr.text((u+10,w-16),v['id'].split('_')[0],fill=c,font=font)
 dr.rectangle((20,20,1300,113),fill='#10191d')
 dr.text((35,30),f"119 / {name} | circles: photo | red crosses: model",fill='white',font=font)
 dr.text((35,62),f"Fit RMS {res['fit_rmse_px']:.2f}px | withheld shoulder RMS {res['holdout_rmse_px']:.2f}px | CONDITIONAL",fill='#ffd966',font=font)
 im.save(B/f'renders/qa/P06_119_{name}_landmarks.png')
# Independent-system check sheet: same camera, no refit to wing tips.
im=Image.open(B/'renders/qa/P06_119_revised_landmarks.png');dr=ImageDraw.Draw(im)
for item in report['cross_system_checks']:
 u,w=item['observed_px'];a,b=item['projected_px'];dr.ellipse((u-6,w-6,u+6,w+6),outline='#ffdb64',width=3);dr.line((u,w,a,b),fill='#ff405e',width=3);dr.line((a-6,b-6,a+6,b+6),fill='#ff405e',width=3);dr.line((a-6,b+6,a+6,b-6),fill='#ff405e',width=3)
 dr.text((u-70,w-45),f"{item['error_px']:.1f}px / OPEN",font=font,fill='#ff405e',stroke_width=1,stroke_fill='white')
im.save(B/'renders/qa/P06_119_cross_system.png')
# Unmodified plan with registered roof footprints overlaid for source checking.
im=Image.open(next((R/'01_Kat_Planlari').rglob('102_*'))).convert('RGB');dr=ImageDraw.Draw(im)
dr.line([tuple(v) for v in outer+[outer[0]]],fill='#cd2350',width=3);dr.line([tuple(v) for v in inner+[inner[0]]],fill='#147da0',width=3)
dr.rectangle((15,865,1090,940),fill='#10191d');dr.text((25,875),'102 / red: roof candidate extent; blue: lantern candidate',fill='white',font=font);dr.text((25,905),'Floor diagram is not a roof survey. No source scaling changed.',fill='#ffd966',font=font)
im.save(B/'renders/qa/P06_plan_check.png')
print(json.dumps({k:{s:v[s] for s in ['fit_rmse_px','holdout_rmse_px','focal_px','camera_parameters']} for k,v in results.items()},indent=2))
