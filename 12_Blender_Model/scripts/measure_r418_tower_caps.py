from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
from scipy.optimize import least_squares
out={}
for t in json.loads((R/'.local_source_cache/r154/fort.json').read_text())['towers']:
 ids=tree.query_ball_point(t['center'],t['radius']-.25);q=p[ids];r=np.linalg.norm(q[:,:2]-t['center'],axis=1);mask=(r>.7)&(q[:,2]>4)&(q[:,2]<8)&np.isin(cl[ids],[1,6]);q=q[mask];r=r[mask];cells=np.floor(q[:,:2]/.4).astype(int);uq=[]
 for cell in np.unique(cells,axis=0):
  a=q[np.all(cells==cell,axis=1)]
  if len(a)>=2 and np.ptp(a[:,2])<.2:uq.append(np.median(a,axis=0))
 q=np.array(uq)
 if len(q)<12:out[t['name']]=dict(valid=False,count=len(q));continue
 r=np.linalg.norm(q[:,:2]-t['center'],axis=1);cc=np.floor(q[:,:2]/.4).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0;A=np.column_stack((np.ones(len(r)),r));fit=least_squares(lambda c:(A@c-q[:,2])[~test],[6,-.2],loss='soft_l1',f_scale=.05);err=(A@fit.x-q[:,2])[test];out[t['name']]=dict(coef=fit.x.tolist(),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(err**2))),max=float(abs(err).max()),valid=bool(np.sqrt(np.mean(err**2))<.1 and abs(err).max()<.25),samples=q.tolist())
(R/'reports/R418_TOWER_CAP_PLANES.json').write_text(json.dumps(out,indent=2));print({k:{a:b for a,b in v.items() if a!='samples'} for k,v in out.items()})
