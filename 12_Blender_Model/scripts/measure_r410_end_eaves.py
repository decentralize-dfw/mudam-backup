from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from shapely.geometry import Polygon,Point
from scipy.optimize import least_squares
raw=json.loads((R/'reports/R388_EARTH_PROFILE.json').read_text());outer=Polygon(raw['outline']);inner=Polygon(raw['inner']);cp=json.loads((R/'reports/R402_LOW_COURT.json').read_text())['sourcePixels'];court=Polygon([(-74.5+x*65/1100,-1.5-y*65/1100) for x,y in cp]);domain=outer.difference(inner).difference(court.buffer(.30));fort=json.loads((R/'.local_source_cache/r154/fort.json').read_text())
for t in fort['towers']:domain=domain.difference(Point(t['center']).buffer(t['radius']+.7))
a=json.loads((R/'reports/R394_TOWER_JUNCTION.json').read_text())['samples'];b=raw['samples'];q=np.unique(np.round(np.array(a+b),5),axis=0);q=q[(q[:,0]+q[:,1]<-94)&shapely.contains(domain,shapely.points(q[:,:2]))];out={}
for name,mask in [('west',q[:,1]-q[:,0]>5.5),('east',(q[:,1]-q[:,0]<=5.5)&(q[:,0]+q[:,1]>-114))]:
 p=q[mask];points=shapely.points(p[:,:2]);di=shapely.distance(points,inner.boundary);do=shapely.distance(points,outer.boundary);cc=np.floor(p[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0
 def calc(c):return np.maximum(c[5],c[0]+c[1]*di-c[2]*np.exp(-np.maximum(0,do-c[4])/c[3]))
 fit=least_squares(lambda c:(calc(c)-p[:,2])[~test],[3.5,-.05,2.1,1.2,.2,1.35],bounds=([2.8,-.5,0,.1,0,1.1],[4.5,.3,4,5,2,1.7]));e=(calc(fit.x)-p[:,2])[test];out[name]=dict(coef=fit.x.tolist(),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25),samples=p.tolist())
(R/'reports/R410_END_EAVE_PROFILES.json').write_text(json.dumps(out,indent=2));print({k:{kk:vv for kk,vv in v.items() if kk!='samples'} for k,v in out.items()})
