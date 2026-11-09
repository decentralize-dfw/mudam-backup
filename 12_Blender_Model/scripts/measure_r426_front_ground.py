from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum));tree=cKDTree(p[:,:2])

rows=[]
for xy in [(-80,-64),(-83,-65),(-85,-65),(-78,-66),(-75,-68),(-73,-70),(-70,-72),(-67,-73),(-82,-61),(-84,-58),(-86,-55),(-88,-52),(-80,-54),(-79,-57),(-76,-59),(-70,-60),(-65,-65)]:
 ids=tree.query_ball_point(xy,.6);q=p[ids];cs=cl[ids];row={'xy':xy,'classes':{}}
 for cls in [1,2,6]:
  z=q[cs==cls,2]
  if len(z):row['classes'][str(cls)]={'n':len(z),'median':float(np.median(z)),'range':[float(z.min()),float(z.max())]}
 rows.append(row)
(R/'reports/R426_FRONT_GROUND_CONTROLS.json').write_text(json.dumps(rows,indent=2));print(rows)
