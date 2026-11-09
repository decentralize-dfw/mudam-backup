from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum));tree=cKDTree(p[:,:2])

paths={'west':[(328,813),(295,816),(263,830),(240,852),(223,879),(218,906),(225,930),(238,953),(256,974),(270,985)],'south':[(285,1014),(305,1045),(329,1070),(357,1091),(388,1101),(418,1099),(446,1087),(465,1066)]};rows=[]
for side,points in paths.items():
 for px,py in points:
  xy=(-120+px*220/1400,95-py*220/1400);ids=tree.query_ball_point(xy,.45);q=p[ids];cs=cl[ids];row={'side':side,'pixel':[px,py],'xy':xy,'classes':{}}
  for cls in [1,2,6]:
   z=q[cs==cls,2]
   if len(z):row['classes'][str(cls)]={'n':len(z),'median':float(np.median(z)),'range':[float(z.min()),float(z.max())]}
  rows.append(row)
(R/'reports/R427_FRONT_COUNTERWALL_CONTROLS.json').write_text(json.dumps(rows,indent=2));print(rows)
