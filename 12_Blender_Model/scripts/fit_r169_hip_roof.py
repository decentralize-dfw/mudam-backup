from pathlib import Path
import sys,json
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from scipy.optimize import least_squares
D=R/'.local_source_cache/r169';data=json.loads((D/'roof_planes_33.json').read_text());p=np.array(data['points']);xmin,ymin=p[:,:2].min(0);xmax,ymax=p[:,:2].max(0);cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
# Convex four-plane upper hip roof. Dormers are positive outliers, not a reason to warp the roof planes.
mask=(p[:,0]>xmin+2)&(p[:,0]<xmax-2)&(p[:,1]>ymin+2)&(p[:,1]<ymax-2);q=p[mask]
def pred(par,pts):
 zr,yr,xl,xr,af,ab,al,ar=par;x,y=pts[:,0],pts[:,1]
 return np.minimum.reduce([zr-af*(y-yr),zr+ab*(y-yr),zr+al*(x-xl),zr-ar*(x-xr)])
def loss(par):
 err=pred(par,q)-q[:,2];return np.where(err<0,err*.5,err)
initial=[np.quantile(q[:,2],.9),cy,cx-4,cx+4,.2,.2,.6,.6];low=[q[:,2].min(),ymin+2,xmin+1,cx,.04,.04,.05,.05];high=[q[:,2].max()+.5,ymax-2,cx,xmax-1,2,2,3,3];fit=least_squares(loss,initial,bounds=(low,high),loss='soft_l1',f_scale=.1,max_nfev=1000);res=pred(fit.x,q)-q[:,2];report=dict(parameters=fit.x.tolist(),sample_count=len(q),median_abs_residual_m=float(np.median(abs(res))),p90_abs_residual_m=float(np.quantile(abs(res),.9)),accepted=False,limits='Upper-roof fit only. Dormers, mansard skirt and eaves excluded. Must compare before using.');(D/'hip_roof_fit_33.json').write_text(json.dumps(report,indent=2));print(report)
