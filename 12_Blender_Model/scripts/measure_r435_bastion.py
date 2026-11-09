from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum));tree=cKDTree(p[:,:2])


f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());out=[]
for tower in f['towers']:
 if tower['name']=='CENTRE':continue
 c=np.array(tower['center']);delta=p[:,:2]-c;rad=np.linalg.norm(delta,axis=1);front=-np.array(f['direction']);angle=np.arccos(np.clip((delta@front)/np.maximum(rad,1e-9),-1,1));mask=(rad>3.8)&(rad<7)&(angle<np.deg2rad(60))&(p[:,2]>-11)&(p[:,2]<1.6)&np.isin(cl,[1,6]);q=p[mask];r=rad[mask];rows=[]
 for z in np.arange(-10,1,.5):
  a=r[(q[:,2]>=z)&(q[:,2]<z+.5)]
  if len(a)>=5:rows.append(dict(z=float(z+.25),n=len(a),radiusQuantiles=np.quantile(a,[.1,.5,.9]).tolist()))
 out.append(dict(tower=tower['name'],rows=rows))
(R/'reports/R435_LOWER_BASTION_RADIAL_CONTROLS.json').write_text(json.dumps(out,indent=2));print(out)
