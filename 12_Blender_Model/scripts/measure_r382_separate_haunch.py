from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np,shapely
from shapely.geometry import Polygon
from scipy.optimize import least_squares
r=json.loads((R/'reports/R343_EARTH_ROOF_ANALYTIC.json').read_text());allq=np.array(r['samples']);inner=Polygon(r['opening']);outer=Polygon(r['outline']);out={}
for name,lo,hi in [('head',-75,100),('stem',-105,-75)]:
 q=allq[(allq[:,0]+allq[:,1]>lo)&(allq[:,0]+allq[:,1]<=hi)];pts=shapely.points(q[:,:2]);di=shapely.distance(pts,inner.boundary);do=shapely.distance(pts,outer.boundary);x=(q[:,0]+45)/30;y=(q[:,1]+35)/30;cc=np.floor(q[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0
 def calc(c):return c[0]+c[1]*x+c[2]*y-c[3]*np.exp(-di/c[4])-c[5]*np.exp(-do/c[6])
 f=least_squares(lambda c:(calc(c)-q[:,2])[~test],[3.5,0,0,1.5,1,1.5,1],bounds=([2,-1,-1,0,.1,0,.1],[5,1,1,3,5,3,5]),max_nfev=1000);e=(calc(f.x)-q[:,2])[test];out[name]=dict(coef=f.x.tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),p95=float(np.quantile(abs(e),.95)),heldout=int(test.sum()),accepted=False)
print(out);(R/'reports/R382_FORT_SEPARATE_HAUNCH.json').write_text(json.dumps(out,indent=2))
