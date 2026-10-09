"""Planar source008 canopy study. Fits existing conditional plane, not a survey camera."""
from pathlib import Path
import numpy as np,json
B=Path(__file__).resolve().parents[1];E=json.loads((B/'config/entry_package.json').read_text())['entry'];C=json.loads((B/'config/foundation.json').read_text())['calibration'];chain=E['chain'];tip=np.array(E['roof_triangle'][1],float);v=np.array(E['roof_triangle'][0])-tip;near_tip=tip+v/np.linalg.norm(v)*E['column_side_m']/C['meters_per_canonical_pixel']
controls=[dict(id='front_left',plan=chain[0],image=[238,1268]),dict(id='left_return',plan=chain[1],image=[318,1302]),dict(id='left_recess',plan=chain[2],image=[734,1353]),dict(id='center_left',plan=chain[3],image=[855,1417]),dict(id='center_right',plan=chain[4],image=[1077,1445]),dict(id='right_recess',plan=chain[5],image=[1323,1428]),dict(id='column_inside',plan=near_tip.tolist(),image=[1417,1132])]
def fit(src,dst):
 def norm(p):
  c=p.mean(axis=0);s=np.sqrt(2)/np.linalg.norm(p-c,axis=1).mean();T=np.array([[s,0,-s*c[0]],[0,s,-s*c[1]],[0,0,1]]);return (T@np.c_[p,np.ones(len(p))].T).T[:,:2],T
 a,ta=norm(np.array(src));b,tb=norm(np.array(dst));A=[]
 for (x,y),(u,v) in zip(a,b):A.extend([[-x,-y,-1,0,0,0,u*x,u*y,u],[0,0,0,-x,-y,-1,v*x,v*y,v]])
 _,_,vh=np.linalg.svd(A);h=np.linalg.inv(tb)@vh[-1].reshape(3,3)@ta;return h/h[2,2]
def project(h,ps):
 q=(h@np.c_[np.array(ps),np.ones(len(ps))].T).T;return q[:,:2]/q[:,2:]
H=fit([q['plan'] for q in controls],[q['image'] for q in controls]);pred=project(H,[q['plan'] for q in controls]);errors=np.linalg.norm(pred-np.array([q['image'] for q in controls]),axis=1)
for q,p,e in zip(controls,pred,errors):q['projection']=p.tolist();q['residual_px']=float(e)
lights=[[622,1301],[972,1267],[1217,1304],[1359,1226],[872,1335],[1100,1365]];positions=project(np.linalg.inv(H),lights);holdout=[]
for i in range(len(controls)):
 c=controls[:i]+controls[i+1:];hh=fit([q['plan'] for q in c],[q['image'] for q in c]);p=project(hh,[controls[i]['plan']])[0];holdout.append(dict(id=controls[i]['id'],error_px=float(np.linalg.norm(p-controls[i]['image']))))
result=dict(source='008',image_size=[1920,2931],plane_z=E['soffit_z'],controls=controls,homography_plan_to_image=H.tolist(),fit_rms_px=float(np.sqrt(np.mean(errors**2))),leave_one_out=holdout,lights=[dict(id=f'CANOPY_{i+1:02d}',image_pixel=p,canonical=xy.tolist()) for i,(p,xy) in enumerate(zip(lights,positions))],status='study_not_released',limits=['Manual corners and visible circular fixtures; no true camera/lens or measured plane calibration.','Reconstruction uses current conditional facade/column plane. Reprojection of fitted landmarks is not independent building accuracy.','Six clearly visible fixture centers selected; tiny uncertain dots excluded. Full count and hidden fixture positions unresolved.']);(B/'reports/R61_canopy_light_study.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
