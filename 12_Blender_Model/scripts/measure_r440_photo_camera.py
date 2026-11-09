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
v0=[-104,-91,-4.5,.66,.13,0];fit=least_squares(resid,v0,max_nfev=1000);err=np.array(resid(fit.x));d=dict(photo='R423_68151060.jpg',fullPhoto='R440_front_full.jpg',focalPixels=focal,cameraParameters=fit.x.tolist(),basis=[v.tolist() for v in basis(fit.x)],rimControls=rows,rmsPixels=float(np.sqrt(np.mean(err**2))),maxPixels=float(abs(err).max()),residuals=err.tolist(),method='Fit camera pose to three independently modeled roof rims using EXIF39mm equivalent focal, original6000px sensor and5838px crop. Principal point assumed centered; rim radii remain prior model dimensions. Not independent validation of tower size.')
(R/'reports/R440_FRONT_PHOTO_CAMERA.json').write_text(json.dumps(d,indent=2));print(d)
