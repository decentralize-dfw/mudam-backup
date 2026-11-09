from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
import shapely
from shapely.geometry import Polygon,Point
from scipy.optimize import least_squares
raw=json.loads((R/'reports/R388_EARTH_PROFILE.json').read_text());outer=Polygon(raw['outline']);inner=Polygon(raw['inner']);f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());domain=outer.difference(inner)
for t in f['towers']:domain=domain.difference(Point(t['center']).buffer(t['radius']+.7))
pts=shapely.points(p[:,:2]);keep=shapely.contains(domain,pts)&np.isin(cl,[1,2,6])&(p[:,2]>1)&(p[:,2]<4.7)&(p[:,0]+p[:,1]<=-99);pp=p[keep];cells=np.floor(pp[:,:2]/.5).astype(int);q=[]
for cell in np.unique(cells,axis=0):
 z=pp[np.all(cells==cell,axis=1)]
 if len(z)>=3 and np.ptp(z[:,2])<.18:q.append(np.median(z,axis=0))
q=np.array(q);pts=shapely.points(q[:,:2]);di=shapely.distance(pts,inner.boundary);do=shapely.distance(pts,outer.boundary);cc=np.floor(q[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0;x=(q[:,0]+60)/10;y=(q[:,1]+50)/10
def calc(c):return c[0]+c[1]*x+c[2]*y-c[3]*np.exp(-do/c[4])-c[5]*np.exp(-di/c[6])
fit=least_squares(lambda c:(calc(c)-q[:,2])[~test],[3.3,0,0,1,.5,.3,.5],bounds=([2,-2,-2,0,.1,0,.1],[4.5,2,2,3,5,2,5]),max_nfev=1000);e=(calc(fit.x)-q[:,2])[test];out=dict(coef=fit.x.tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),heldout=int(test.sum()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25),samples=q.tolist(),method='Independent curved tower-end shoulder, tower bodies excluded, no source geometry transferred.');(R/'reports/R394_TOWER_JUNCTION.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='samples'})
