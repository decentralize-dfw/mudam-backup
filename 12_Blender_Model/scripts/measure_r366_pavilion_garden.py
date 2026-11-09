from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
import shapely
from shapely.geometry import Polygon
from scipy.optimize import least_squares
px=[(190,529),(425,335),(440,300),(560,230),(604,188),(680,180),(889,190),(884,410),(820,450),(700,500),(610,535),(450,585),(245,650)]
hole=[(446,320),(485,278),(645,278),(689,320),(689,458),(645,501),(485,501),(446,458)]
conv=lambda pts:[[-5.5+x*.0625,-18.75-y*.0625] for x,y in pts]
poly=Polygon(conv(px),[conv(hole)]);b=poly.bounds;keep=(p[:,0]>b[0])&(p[:,0]<b[2])&(p[:,1]>b[1])&(p[:,1]<b[3])&(cl==2)&(p[:,2]>-7.5)&(p[:,2]<-2);q=p[keep];q=q[shapely.contains_xy(poly.buffer(-.2),q[:,0],q[:,1])];cells={}
for pt in q:cells.setdefault(tuple(np.floor(pt[:2]/.6).astype(int)),[]).append(pt)
q=np.array([np.median(v,axis=0) for v in cells.values() if len(v)>=3 and np.ptp(np.array(v)[:,2])<.18]);A=np.column_stack([q[:,:2],np.ones(len(q))]);cc=np.floor(q[:,:2]/.6).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0
co=[.03,0,-6.5,.07,-.113,-13.18]
def predict(c):return np.maximum(A@c[:3],A@c[3:])
f=least_squares(lambda c:(predict(c)-q[:,2])[~test],co,max_nfev=1000);e=(predict(f.x)-q[:,2])[test]
out=dict(outline=conv(px),hole=conv(hole),planes=f.x.reshape(2,3).tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),heldout=int(test.sum()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25),controls=q.tolist());print({k:v for k,v in out.items() if k!='controls'});(R/'reports/R366_PAVILION_GARDEN.json').write_text(json.dumps(out,indent=2))
