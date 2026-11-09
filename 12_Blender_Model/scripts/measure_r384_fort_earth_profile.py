from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np,shapely
from shapely.geometry import Polygon
from scipy.optimize import least_squares
r=json.loads((R/'reports/R343_EARTH_ROOF_ANALYTIC.json').read_text());q=np.array(r['samples']);inner=Polygon(r['opening']);di=shapely.distance(shapely.points(q[:,:2]),inner.boundary);keep=(di>1.5)&(q[:,0]+q[:,1]>-107);q=q[keep];di=di[keep];x=(q[:,0]+45)/30;y=(q[:,1]+35)/30;cc=np.floor(q[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0
# Raised inner parapet separates lower metal-edge ledge from earth cover.
def calc(c):return c[0]+c[1]*x+c[2]*y+c[3]*di+c[4]*np.maximum(0,di-c[5])
f=least_squares(lambda c:(calc(c)-q[:,2])[~test],[3.7,0,0,-.15,-.6,3.4],bounds=([2,-1,-1,-1,-2,1.5],[5,1,1,.5,0,6]),max_nfev=1000);e=(calc(f.x)-q[:,2])[test];out=dict(coef=f.x.tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),p95=float(np.quantile(abs(e),.95)),heldout=int(test.sum()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25),method='Independent raised earth roof: shallow inner pitch and steep outer pitch with one breakline, separated from lower metal perimeter ledge; profile inferred from R383 classified cross-section.');print(out);(R/'reports/R384_FORT_PITCHED_EARTH_ROOF.json').write_text(json.dumps(out,indent=2))
