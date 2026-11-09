from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum));tree=cKDTree(p[:,:2])
rows=[]
for file in ['R327_NORTH_OUTER_MOAT_LEVELS.json','R326_NORTH_CHAMBER_LEVELS.json','R325_RUIN_DOMAINS.json']:
 for s in json.loads((R/'reports'/file).read_text())['source']:
  ids=tree.query_ball_point(s['xy'],.35);q=p[ids];c=cl[ids];groups={}
  for cls in sorted(set(c)):
   z=q[c==cls,2];groups[str(cls)]=dict(count=len(z),median=float(np.median(z)),min=float(z.min()),max=float(z.max()))
  rows.append(dict(sourceFile=file,name=s['name'],xy=s['xy'],scanZ=s['medianZ'],scanRange=s['spread'],lidarClasses=groups))
(R/'reports/R328_LIDAR_INDEPENDENT_LEVELS.json').write_text(json.dumps(dict(radiusM=.35,datum=datum,rows=rows,method='Independent classified ACT2024 returns within 0.35m. Raw returns only, no triangulation or scan surface transferred.'),indent=2));print([(r['name'],round(r['scanZ'],2),r['lidarClasses']) for r in rows])
