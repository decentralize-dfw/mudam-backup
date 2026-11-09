from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
import shapely
from shapely.geometry import Polygon
domains=[('north_nw',[(228,445),(770,122),(789,166),(250,479)],'north'),('north_ne',[(789,166),(810,146),(1073,630),(1045,631)],'north'),('east_north',[(389,12),(408,-22),(888,148),(858,194)],'east'),('east_side_upper',[(858,194),(900,200),(794,440),(740,443)],'east'),('east_side_middle',[(740,443),(794,440),(732,580),(670,580)],'east'),('east_side_lower',[(670,580),(732,580),(666,730),(600,719)],'east')]
result={}
for name,pixels,zone in domains:
 convert=(lambda a:(-57+a[0]*44/1200,84.5-a[1]*44/1200)) if zone=='north' else (lambda a:(39+a[0]*42/1200,-14.25-a[1]*42/1200))
 outline=[convert(a) for a in pixels];poly=Polygon(outline).buffer(-.12);b=poly.bounds
 keep=(p[:,0]>b[0])&(p[:,0]<b[2])&(p[:,1]>b[1])&(p[:,1]<b[3])&np.isin(cl,[1,2])&(p[:,2]>-5)&(p[:,2]<-1.5)
 q=p[keep];q=q[shapely.contains_xy(poly,q[:,0],q[:,1])];cells={}
 for pt in q:cells.setdefault(tuple(np.floor(pt[:2]/.6).astype(int)),[]).append(pt)
 controls=np.array([np.median(v,axis=0) for v in cells.values() if len(v)>=3 and np.ptp(np.array(v)[:,2])<.18])
 if len(controls)<12:result[name]=dict(valid=False,count=len(controls));continue
 A=np.column_stack([controls[:,:2],np.ones(len(controls))]);cc=np.floor(controls[:,:2]/.6).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0;train=~test
 coef=np.linalg.lstsq(A[train],controls[train,2],rcond=None)[0]
 for _ in range(3):
  good=train&(abs(A@coef-controls[:,2])<.15);coef=np.linalg.lstsq(A[good],controls[good,2],rcond=None)[0]
 residual=A[test]@coef-controls[test,2];rms=float(np.sqrt(np.mean(residual**2)));mx=float(abs(residual).max())
 result[name]=dict(outline=outline,plane=coef.tolist(),valid=bool(rms<.1 and mx<.25 and test.sum()>=4),rms=rms,maxAbsolute=mx,heldOut=int(test.sum()),training=int(good.sum()),controls=controls.tolist(),source='Independent planar moat floor, ACT2024 stable classified ground cells; polygon from source-matched views, no source faces.')
(R/'reports/R335_OUTER_MOAT_REMAINDER.json').write_text(json.dumps(result,indent=2));print({k:{a:b for a,b in v.items() if a!='controls'} for k,v in result.items()})
