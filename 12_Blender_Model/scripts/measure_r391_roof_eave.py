from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from shapely.geometry import Polygon
from scipy.optimize import least_squares
r=json.loads((R/'reports/R388_EARTH_PROFILE.json').read_text());q0=np.array(r['samples']);inner=Polygon(r['inner']);outer=Polygon(r['outline']);out={}
for name,mask in [('north_head',q0[:,1]>-14),('east_head',(q0[:,0]>-22)&(q0[:,1]<=-14))]:
 q=q0[mask];pts=shapely.points(q[:,:2]);di=shapely.distance(pts,inner.boundary);do=shapely.distance(pts,outer.boundary);cc=np.floor(q[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0
 def calc(c):return np.maximum(c[5],c[0]+c[1]*di-c[2]*np.exp(-np.maximum(0,do-c[4])/c[3]))
 fit=least_squares(lambda c:(calc(c)-q[:,2])[~test],[3.5,-.03,2.5,1.4,.3,1.3],bounds=([3,-.6,0,.1,0,1.1],[4,.1,5,4,1.2,1.6]),max_nfev=1000);e=(calc(fit.x)-q[:,2])[test];out[name]=dict(coef=fit.x.tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),p95=float(np.quantile(abs(e),.95)),heldout=int(test.sum()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25),outliers=[dict(point=a.tolist(),error=float(b)) for a,b in zip(q[test],e) if abs(b)>.25])
(R/'reports/R391_EAVE_PROFILE.json').write_text(json.dumps(out,indent=2));print(out)
