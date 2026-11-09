from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
import shapely
from shapely.geometry import Polygon
domains=[('moat_inner_arm',[(160,402),(388,235),(414,305),(188,468)],[1,6],[-4.3,-3.7])]
result={}
for name,pixels,classes,zlim in domains:
 outline=[[-5.5+x*.0625,-18.75-y*.0625] for x,y in pixels];poly=Polygon(outline).buffer(-.18);b=poly.bounds
 keep=(p[:,0]>b[0])&(p[:,0]<b[2])&(p[:,1]>b[1])&(p[:,1]<b[3])&np.isin(cl,classes)&(p[:,2]>zlim[0])&(p[:,2]<zlim[1]);q=p[keep];q=q[shapely.contains_xy(poly,q[:,0],q[:,1])];cells={}
 for pt in q:cells.setdefault(tuple(np.floor(pt[:2]/.6).astype(int)),[]).append(pt)
 controls=np.array([np.median(v,axis=0) for v in cells.values() if len(v)>=3 and np.ptp(np.array(v)[:,2])<.18])
 if len(controls)<12:result[name]=dict(valid=False,count=len(controls));continue
 A=np.column_stack([controls[:,:2],np.ones(len(controls))]);cc=np.floor(controls[:,:2]/.6).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0;train=~test;coef=np.linalg.lstsq(A[train],controls[train,2],rcond=None)[0]
 residual=A[test]@coef-controls[test,2];rms=float(np.sqrt(np.mean(residual**2)));mx=float(abs(residual).max())
 result[name]=dict(outline=outline,plane=coef.tolist(),valid=bool(rms<.1 and mx<.25 and test.sum()>=4),rms=rms,maxAbsolute=mx,heldOut=int(test.sum()),training=int(train.sum()),controls=controls.tolist(),source='R345 source outline and independent ACT2024 classified stable spatial cells; architectural plane, no sampled surface.')
(R/'reports/R360_PAVILION_PLANES.json').write_text(json.dumps(result,indent=2));print({k:{a:b for a,b in v.items() if a!='controls'} for k,v in result.items()})
