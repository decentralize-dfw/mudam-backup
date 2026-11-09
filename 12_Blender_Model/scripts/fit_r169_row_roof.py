from pathlib import Path
import sys,json
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from shapely.geometry import Polygon
from shapely import contains_xy
D=R/'.local_source_cache/r169';b=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][2];a=np.load(D/(b['id']+'.npz'));xx,yy=np.meshgrid(a['x'],a['y']);ang=float(a['angle']);wx=xx*np.cos(ang)-yy*np.sin(ang);wy=xx*np.sin(ang)+yy*np.cos(ang);mask=contains_xy(Polygon(b['rings'][0]),wx,wy)&np.isfinite(a['z'])&(a['z']>b['base']+3);points=np.column_stack([xx[mask],yy[mask],a['z'][mask]]);remaining=np.arange(len(points));rng=np.random.default_rng(169);planes=[]
for step in range(6):
 if len(remaining)<45:break
 pts=points[remaining];best=None;bestcount=0
 for _ in range(700):
  seed=pts[rng.choice(len(pts),3,replace=False)];A=np.c_[seed[:,:2],np.ones(3)]
  if abs(np.linalg.det(A))<.1:continue
  c=np.linalg.solve(A,seed[:,2])
  if np.linalg.norm(c[:2])>3:continue
  hit=abs(pts[:,2]-(np.c_[pts[:,:2],np.ones(len(pts))]@c))<.13;count=int(hit.sum())
  if count>bestcount:bestcount=count;best=hit
 if bestcount<45:break
 c=np.linalg.lstsq(np.c_[pts[best,:2],np.ones(bestcount)],pts[best,2],rcond=None)[0];ids=remaining[best];planes.append(dict(coeff=c.tolist(),count=bestcount,indices=ids.tolist(),rmse=float(np.sqrt(np.mean((np.c_[pts[best,:2],np.ones(bestcount)]@c-pts[best,2])**2)))))
 remaining=remaining[~best]
(D/'roof_planes_164179202.json').write_text(json.dumps(dict(id=b['id'],points=points.tolist(),planes=planes,unassigned=remaining.tolist(),sample_grid_m=.4,fit_tolerance_m=.13),indent=2));print([(p['count'],p['coeff'],p['rmse']) for p in planes]);print('unassigned',len(remaining),'total',len(points))


