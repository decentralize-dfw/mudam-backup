from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
import shapely
from shapely.geometry import Polygon
result={}
for label,file,convert in [('north','R326_NORTH_RUIN_PLAN.json',lambda a:(-57+a[0]*44/1200,84.5-a[1]*44/1200)),('east','R327_EAST_RUIN_PLAN.json',lambda a:(39+a[0]*42/1200,-14.25-a[1]*42/1200))]:
 report=json.loads((R/'reports'/file).read_text());poly=Polygon([convert(a) for a in report['outline']],[ [convert(a) for a in h] for h in report['recesses']])
 # Edge bands exclude central planted court and mixed vertical returns.
 band=poly.boundary.buffer(.45).intersection(poly.buffer(-.12))
 bounds=poly.bounds;keep=(p[:,0]>bounds[0])&(p[:,0]<bounds[2])&(p[:,1]>bounds[1])&(p[:,1]<bounds[3])&np.isin(cl,[1,6])&(p[:,2]>-.7)&(p[:,2]<.7)
 q=p[keep];q=q[shapely.contains_xy(band,q[:,0],q[:,1])];cells={}
 for point in q:cells.setdefault(tuple(np.floor(point[:2]/.6).astype(int)),[]).append(point)
 controls=[]
 for key,values in cells.items():
  values=np.array(values)
  if len(values)>=3 and np.ptp(values[:,2])<.15:controls.append(np.median(values,axis=0))
 controls=np.array(controls);A=np.column_stack([controls[:,:2],np.ones(len(controls))]);cell=np.floor(controls[:,:2]/.6).astype(int);test=(cell[:,0]+3*cell[:,1])%4==0;train=~test
 coef=np.linalg.lstsq(A[train],controls[train,2],rcond=None)[0]
 for _ in range(3):
  good=train&(np.abs(A@coef-controls[:,2])<.12);coef=np.linalg.lstsq(A[good],controls[good,2],rcond=None)[0]
 residual=A[test]@coef-controls[test,2]
 result[label]=dict(plane=coef.tolist(),controls=len(controls),training=int(good.sum()),heldOut=len(residual),rms=float(np.sqrt(np.mean(residual**2))),maxAbsolute=float(abs(residual).max()),validSinglePlane=bool(np.sqrt(np.mean(residual**2))<.1 and abs(residual).max()<.25),method='Architectural plane from classified stable coping cells; held-out cells not fitted; no cloud faces used.')
(R/'reports/R329_COPING_PLANES.json').write_text(json.dumps(result,indent=2));print(result)
