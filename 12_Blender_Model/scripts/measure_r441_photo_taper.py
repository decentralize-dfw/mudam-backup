import json,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from scipy.optimize import least_squares
focal=6000*39/36*1280/5838
# Manually identified outer cornice/roof rim silhouette bounds on1280px original photo.
rows=[('WEST',[-71.5,-47.6],4.67,6.078584186-.2027358223*4.67,[130,451,164,210]),('CENTRE',[-61.6,-53.15],2.97,5.897931623-.293983576*2.97,[573,728,203,238]),('SOUTH',[-57.4,-63.1],4.67,5.998018003-.2248846902*4.67,[851,1148,162,211])]
def basis(v):
 yaw,pitch,roll=v[3:];forward=np.array([math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)]);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);return right*math.cos(roll)+up*math.sin(roll),up*math.cos(roll)-right*math.sin(roll),forward
def project(v,pts):
 right,up,forward=basis(v);q=pts-v[:3];depth=q@forward;return np.c_[640+focal*(q@right)/depth,420-focal*(q@up)/depth]
def circles():
 a=np.linspace(0,2*np.pi,720,endpoint=False)
 return [np.c_[c[0]+r*np.cos(a),c[1]+r*np.sin(a),np.full(len(a),z)] for name,c,r,z,b in rows]
pts=circles()
def resid(v):
 rr=[]
 for p,row in zip(pts,rows):
  q=project(v,p);rr.extend(np.array([q[:,0].min(),q[:,0].max(),q[:,1].min(),q[:,1].max()])-row[-1])
 return rr

d=json.loads((R/'reports/R440_FRONT_PHOTO_CAMERA.json').read_text());cam=np.array(d['cameraParameters']);observations={'WEST':[[138,370],[128,420],[118,470],[110,520],[101,570],[96,600]],'SOUTH':[[1130,370],[1140,420],[1150,470],[1160,520],[1170,570],[1175,600]]};out=[]
for name,c,_,_,_ in rows:
 if name not in observations:continue
 obs=np.array(observations[name]);delta=cam[:2]-c;D=np.linalg.norm(delta);phi=np.arctan2(delta[1],delta[0])
 def predicted(v):
  a,b=v;ang=np.arccos(np.clip((a+b*cam[2])/D,-.99,.99));options=[]
  for theta in [phi-ang,phi+ang]:
   z=np.array([-12,2]);r=a+b*z;p=np.c_[c[0]+r*np.cos(theta),c[1]+r*np.sin(theta),z];q=project(cam,p);x=q[0,0]+(obs[:,1]-q[0,1])*(q[1,0]-q[0,0])/(q[1,1]-q[0,1]);options.append(x)
  return np.minimum(*options) if name=='WEST' else np.maximum(*options)
 fit=least_squares(lambda v:predicted(v)-obs[:,0],[4.4,-.1],bounds=([2,-.4],[7,0]));err=predicted(fit.x)-obs[:,0];out.append(dict(tower=name,radiusAtZ0=float(fit.x[0]),radiusSlope=float(fit.x[1]),observations=obs.tolist(),rmsPixels=float(np.sqrt(np.mean(err**2))),limits='Single photo silhouette fit conditioned on approximate R440 camera and inherited tower centers. Not accepted geometry; independent LiDAR comparison required.'))
(R/'reports/R441_PHOTO_BASTION_TAPER.json').write_text(json.dumps(out,indent=2));print(out)
