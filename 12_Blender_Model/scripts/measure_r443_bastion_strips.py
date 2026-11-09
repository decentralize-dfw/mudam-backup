from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum));tree=cKDTree(p[:,:2])


from scipy.optimize import least_squares
f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());out=[]
for tower in f['towers']:
 if tower['name']=='CENTRE':continue
 c=np.array(tower['center']);delta=p[:,:2]-c;rad=np.linalg.norm(delta,axis=1);front=-np.array(f['direction']);angle=np.arccos(np.clip((delta@front)/np.maximum(rad,1e-9),-1,1));mask=(rad>2.8)&(rad<7)&(angle<np.deg2rad(15))&(p[:,2]>-9.5)&(p[:,2]<-1.0)&((p[:,2]<-6.5)|(p[:,2]>-3))&np.isin(cl,[1,6]);q=p[mask]
 # Spatial cell medians avoid counting repeated returns as independent constraints.
 cells={}
 for v in q:cells.setdefault(tuple(np.floor(v/.35).astype(int)),[]).append(v)
 q=np.array([np.median(v,axis=0) for v in cells.values()]);keys=np.floor(q/.35).astype(int);test=(keys[:,0]+3*keys[:,1]+5*keys[:,2])%5==0
 def residual(v,Q):return np.linalg.norm(Q[:,:2]-v[:2],axis=1)-(v[2]+v[3]*Q[:,2])
 fit=least_squares(lambda v:residual(np.r_[c,v],q[~test]),[4,-.15],bounds=([2,-.4],[6,0]));fit.x=np.r_[c,fit.x]
 e=residual(fit.x,q[test]);row=dict(tower=tower['name'],fit=fit.x.tolist(),training=int((~test).sum()),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),quantiles=np.quantile(abs(e),[.5,.9,.95]).tolist());row['scope']='Narrow front15degree solid masonry strip; exclude middle opening band before fitting; not whole circumference acceptance';row['valid']=row['rms']<.1 and row['max']<.25;out.append(row)
(R/'reports/R443_BASTION_FRONT_STRIP_FITS.json').write_text(json.dumps(out,indent=2));print(out)
