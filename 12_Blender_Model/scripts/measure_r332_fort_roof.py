from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
import ast,shapely
from shapely.geometry import Polygon
result={}
for _ in [0]:
 fort=json.loads((R/'.local_source_cache/r154/fort.json').read_text());regions=[('R154_FORT_METAL_ROOF',fort['metal_outline'])];convert=lambda a:a
 for name,points in regions:
  poly=Polygon([convert(a) for a in points]).buffer(-1.0);b=poly.bounds
  keep=(p[:,0]>b[0])&(p[:,0]<b[2])&(p[:,1]>b[1])&(p[:,1]<b[3])&np.isin(cl,[1,2,6])&(p[:,2]>0)&(p[:,2]<5)
  q=p[keep];q=q[shapely.contains_xy(poly,q[:,0],q[:,1])];cells={}
  for pt in q:cells.setdefault(tuple(np.floor(pt[:2]/.4).astype(int)),[]).append(pt)
  controls=np.array([np.median(v,axis=0) for v in cells.values() if len(v)>=3 and np.ptp(np.array(v)[:,2])<.12])
  if len(controls)<12:result[name]={'accepted':False,'reason':'Insufficient stable cells','count':len(controls)};continue
  A=np.column_stack([controls[:,:2],np.ones(len(controls))]);cc=np.floor(controls[:,:2]/.4).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0;train=~test
  coef=np.linalg.lstsq(A[train],controls[train,2],rcond=None)[0]
  for _ in range(3):
   good=train&(abs(A@coef-controls[:,2])<.12);coef=np.linalg.lstsq(A[good],controls[good,2],rcond=None)[0]
  residual=A[test]@coef-controls[test,2];rms=float(np.sqrt(np.mean(residual**2)));mx=float(abs(residual).max())
  result[name]=dict(plane=coef.tolist(),accepted=bool(rms<.08 and mx<.2 and test.sum()>=4),rms=rms,maxAbsolute=mx,heldOut=int(test.sum()),training=int(good.sum()),controls=controls.tolist())
(R/'reports/R332_FORT_ROOF_PLANE.json').write_text(json.dumps(result,indent=2));print({k:{a:b for a,b in v.items() if a!='controls'} for k,v in result.items()})
