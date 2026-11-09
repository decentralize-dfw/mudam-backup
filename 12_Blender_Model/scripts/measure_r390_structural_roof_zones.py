from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from shapely.geometry import Polygon
from scipy.optimize import least_squares
r=json.loads((R/'reports/R388_EARTH_PROFILE.json').read_text());allq=np.array(r['samples']);inner=Polygon(r['inner']);outer=Polygon(r['outline']);out={}
# Structural zones are the two long arms and the two head shoulders. The
# low tower-end junction is a separate physical surface, not fitted as earth.
for name,mask in [('north_head',allq[:,1]>-14),('east_head',(allq[:,0]>-22)&(allq[:,1]<=-14)),('west_arm',(allq[:,0]<=-22)&(allq[:,1]<=-14)&(allq[:,1]-allq[:,0]>6)&(allq[:,0]+allq[:,1]>-100)),('east_arm',(allq[:,0]<=-22)&(allq[:,1]<=-14)&(allq[:,1]-allq[:,0]<=6)&(allq[:,0]+allq[:,1]>-100))]:
 q=allq[mask];pts=shapely.points(q[:,:2]);di=shapely.distance(pts,inner.boundary);do=shapely.distance(pts,outer.boundary);cc=np.floor(q[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0
 def calc(c):return c[0]+c[1]*di-c[2]*np.exp(-do/c[3])
 f=least_squares(lambda c:(calc(c)-q[:,2])[~test],[3.5,-.15,2,.7],bounds=([3,-.6,0,.1],[4,0,4,4]));e=(calc(f.x)-q[:,2])[test];out[name]=dict(coef=f.x.tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),p95=float(np.quantile(abs(e),.95)),heldout=int(test.sum()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25),outliers=[dict(point=a.tolist(),error=float(b)) for a,b in zip(q[test],e) if abs(b)>.25])
(R/'reports/R390_STRUCTURAL_ROOF_ZONES.json').write_text(json.dumps(out,indent=2));print(out)
