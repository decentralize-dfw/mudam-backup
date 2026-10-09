"""A10 conditional source065 ray/plane study; not independent metric camera recovery."""
from pathlib import Path
import numpy as np,json,math
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];s=C['meters_per_canonical_pixel'];origin=np.array([289.5,347.3]);camera_xy=(np.array([242.,278.])-origin)*s
# Atlas camera region is an unverified prior. Two far-corner landmarks depend on R27/R36 candidates.
landmarks=[dict(id='far_corner_head',canonical=[289.5,534.7],z=3.45,image=[552,509]),dict(id='far_corner_inset_foot',canonical=[289.5+1.25/s/math.sqrt(2),534.7-1.25/s/math.sqrt(2)],z=0,image=[486,658])]
rects=[dict(id='SIDE_NEAR',pixels=[[43,955],[125,928],[125,1082],[43,1110]]),dict(id='SIDE_FAR',pixels=[[280,877],[326,862],[326,977],[280,994]])]
def basis(q):
 yaw,pitch,z=q;F=np.array([math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),math.sin(pitch)]);R=np.array([-math.cos(yaw),math.sin(yaw),0]);U=np.array([-math.sin(yaw)*math.sin(pitch),-math.cos(yaw)*math.sin(pitch),math.cos(pitch)]);return R,U,F,np.r_[camera_xy,z]
def project(q,f,pts):
 R,U,F,cam=basis(q);d=np.array(pts)-cam;return np.c_[960+f*(d@R)/(d@F),656.5-f*(d@U)/(d@F)]
pts=[np.r_[(np.array(p['canonical'])-origin)*s,p['z']] for p in landmarks];target=np.array([p['image'] for p in landmarks])
def fit(f,constrain_height=False):
 q=np.array([-.08,-.04,1.65])
 for _ in range(80):
  e=(project(q,f,pts)-target).ravel();J=np.column_stack([((project(q+np.eye(3)[i]*1e-5,f,pts)-target).ravel()-e)/1e-5 for i in range(2 if constrain_height else 3)]);step=np.linalg.lstsq(J,e,rcond=None)[0];q[:len(step)]-=step
  if np.linalg.norm(step)<1e-9:break
 R,U,F,cam=basis(q);windows=[]
 for item in rects:
  world=[]
  for x,y in item['pixels']:
   ray=F+R*(x-960)/f-U*(y-656.5)/f;t=-cam[0]/ray[0];p=cam+ray*t;world.append(p.tolist())
  p=np.array(world);windows.append(dict(id=item['id'],plane_intersections=world,canonical_y_edges=[float(origin[1]+p[[0,3],1].mean()/s),float(origin[1]+p[[1,2],1].mean()/s)],head_z=float(p[:2,2].mean()),sill_z=float(p[2:,2].mean()),width_m=float(abs(p[[1,2],1].mean()-p[[0,3],1].mean())),height_m=float(p[:2,2].mean()-p[2:,2].mean()),head_nonlevel_m=float(np.ptp(p[:2,2])),sill_nonlevel_m=float(np.ptp(p[2:,2]))))
 return dict(focal_px=f,camera_yaw_pitch_height=q.tolist(),camera_canonical_xy=[242,278],projection=project(q,f,pts).tolist(),fit_rms_px=float(np.sqrt(np.mean((project(q,f,pts)-target)**2))),windows=windows)
result=dict(source='065',image_size=[1920,1313],wall_canonical_x=289.5,landmarks=landmarks,manual_openings=rects,studies=[fit(f,True) for f in [1300.,1550.,1800.]],rejected_unbounded_height=[fit(f) for f in [1300.,1550.,1800.]],limits=['Camera XY is the atlas region hypothesis, not a surveyed pose.','Far corner/head/inset foot are ambiguous photo picks based on conditional existing R27/R36 geometry.','Focal1300-1800px is a sensitivity range, not calibrated EXIF/lens/crop.','Window ray intersections test plausibility only. No measured window dimensions, interiors or independent camera validation.']);(B/'reports/A10_side_window_study.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result['studies'],indent=2))
