from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum));tree=cKDTree(p[:,:2])



from scipy.optimize import least_squares
f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());old=json.loads((R/'reports/R418_TOWER_CAP_PLANES.json').read_text());out=[]
for tower in f['towers']:
 c=np.array(tower['center']);r=np.linalg.norm(p[:,:2]-c,axis=1);coef=old[tower['name']]['coef'];mask=(r<6)&(r>.4)&(p[:,2]>3.8)&(p[:,2]<6.5)&(np.abs(p[:,2]-(coef[0]+coef[1]*r))<.25)&np.isin(cl,[1,6]);q=p[mask]
 def residual(v):return v[2]+v[3]*np.linalg.norm(q[:,:2]-v[:2],axis=1)-q[:,2]
 fit=least_squares(residual,[*c,*coef],bounds=([c[0]-1,c[1]-1,5,-.6],[c[0]+1,c[1]+1,8,-.05]),loss='soft_l1',f_scale=.05);dist=np.linalg.norm(q[:,:2]-fit.x[:2],axis=1);angle=np.arctan2(q[:,1]-fit.x[1],q[:,0]-fit.x[0]);rows=[]
 for i in range(16):
  sel=(angle>=-np.pi+i*np.pi/8)&(angle< -np.pi+(i+1)*np.pi/8)&(np.abs(residual(fit.x))<.10)
  if sel.sum()>=4:rows.append(dict(sector=i,n=int(sel.sum()),edge=float(np.quantile(dist[sel],.95))))
 out.append(dict(tower=tower['name'],fit=fit.x.tolist(),sectors=rows,limits='Edge statistics of available roof-class points, not exact eave survey. Missing point coverage can underestimate edge.'))
(R/'reports/R444_TOWER_ROOF_EDGE_DIAGNOSTIC.json').write_text(json.dumps(out,indent=2));print(out)
