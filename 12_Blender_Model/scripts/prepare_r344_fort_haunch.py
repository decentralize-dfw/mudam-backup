from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
import shapely
from shapely.geometry import Polygon,Point
f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());r=json.loads((R/'reports/R340_ROOF_BUILD_INPUT.json').read_text());outer=Polygon(f['footprint']);inner=Polygon(r['roofOutline']);domain=outer.difference(inner.buffer(.15))
for tower in f['towers']:domain=domain.difference(Point(tower['center']).buffer(tower['radius']+.5))
b=domain.bounds;keep=(p[:,0]>b[0])&(p[:,0]<b[2])&(p[:,1]>b[1])&(p[:,1]<b[3])&np.isin(cl,[1,2,6])&(p[:,2]>1.5)&(p[:,2]<5.5);q=p[keep];q=q[shapely.contains_xy(domain,q[:,0],q[:,1])];q=q[(q[:,0]+q[:,1]>-107)&(shapely.distance(shapely.points(q[:,:2]),outer.boundary)>.8)];cells={}
for pt in q:cells.setdefault(tuple(np.floor(pt[:2]/.5).astype(int)),[]).append(pt)
controls=np.array([np.median(v,axis=0) for v in cells.values() if len(v)>=3 and np.ptp(np.array(v)[:,2])<.16]);pt=shapely.points(controls[:,:2]);di=shapely.distance(pt,inner.boundary);do=shapely.distance(pt,outer.boundary);t=di/(di+do);x=(controls[:,0]+45)/30;y=(controls[:,1]+35)/30
A=np.column_stack([np.ones(len(x)),t,t*t,x,y,x*t,y*t]);cc=np.floor(controls[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0;training=~test;coef=np.linalg.lstsq(A[training],controls[training,2],rcond=None)[0]
for _ in range(5):
 good=training&(abs(A@coef-controls[:,2])<.3);coef=np.linalg.lstsq(A[good],controls[good,2],rcond=None)[0]
res=A[test]@coef-controls[test,2]
out=dict(coefficients=coef.tolist(),controls=len(controls),training=int(good.sum()),heldOut=int(test.sum()),heldOutRMS=float(np.sqrt(np.mean(res**2))),heldOutP95=float(np.quantile(abs(res),.95)),heldOutMax=float(abs(res).max()),method='Independent seven-coefficient architectural haunch: z=a+b*t+c*t²+d*x+e*y+f*x*t+g*y*t; t is normalized distance between roof opening and exterior wall. No mesh sampled or source faces transferred.',samples=controls.tolist(),outline=f['footprint'],opening=r['roofOutline'])
(R/'reports/R344_EARTH_HAUNCH_ANALYTIC.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ['samples','outline','opening']})
