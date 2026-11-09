from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum));tree=cKDTree(p[:,:2])


rows=[]
for px,py in [(400,250),(400,300),(480,270),(520,270),(560,270),(600,270),(650,290),(650,310),(570,310),(520,340),(490,370),(750,245),(750,280),(750,310)]:
 xy=np.array([-120+px*220/1400,95-py*220/1400]);ids=tree.query_ball_point(xy,.65);q=p[ids];c=cl[ids]
 rows.append(dict(pixel=[px,py],xyz=[*xy,float(np.median(q[c==2,2])) if (c==2).sum() else None],groundCount=int((c==2).sum()),classes={str(k):dict(n=int((c==k).sum()),z=np.quantile(q[c==k,2],[0,.5,1]).tolist()) for k in np.unique(c)}))
(R/'reports/R454_LOADING_COURT_LEVELS.json').write_text(json.dumps(rows,indent=2));print(rows)
