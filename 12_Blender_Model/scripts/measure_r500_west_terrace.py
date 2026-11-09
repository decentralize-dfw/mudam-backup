from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum))
line=np.array([[40.95218,-77.7534],[45.79894,-67.27373],[45.44239,-59.34561],[49.04445,-58.95946]])
rows=[]
for k,(a,b) in enumerate(zip(line,line[1:])):
 t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]]);delta=p[:,:2]-a;s=delta@t;o=delta@n
 for u in np.arange(.5,np.linalg.norm(b-a),1):
  rec=dict(segment=k,s=float(u),axis=(a+u*t).tolist(),samples=[])
  for off in [-2,-1,0,1,2]:
   for c in [1,2,6]:
    q=p[(abs(s-u)<.5)&(abs(o-off)<.45)&(cl==c)]
    if len(q):rec['samples'].append(dict(offset=off,classification=c,n=len(q),z=np.quantile(q[:,2],[.1,.5,.9]).tolist()))
  rows.append(rec)
(R/'reports/R500_WEST_TERRACE_SECTIONS.json').write_text(json.dumps(rows,indent=2))
for r in rows:print(r['segment'],round(r['s'],1),[(e['offset'],e['classification'],e['n'],[round(z,2) for z in e['z']]) for e in r['samples']])
