from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,rasterio,pyproj
from scipy.ndimage import map_coordinates
def refine(t):
 a,b,c=t;ls=[sum((p[i]-q[i])**2 for i in (0,1)) for p,q in [(a,b),(b,c),(c,a)]]
 if max(ls)<=2.25:return [t]
 p,q,r=[(a,b,c),(b,c,a),(c,a,b)][ls.index(max(ls))];m=[(p[i]+q[i])/2 for i in (0,1)]
 return refine([p,m,r])+refine([m,q,r])
d=json.loads((R/'config/r177_road_union.json').read_text());points=set()
for t in [t for r in d['surfaces'] for t in r['triangles']]+d['markings']:
 for tri in refine(t):points.update(tuple(round(v,6) for v in p) for p in tri)
points=sorted(points);xy=np.array(points)
with rasterio.open(R/'references/terrain_lidar2024/mudam_extended_mnt_2024.tif') as f:
 a=f.read(1);tr=pyproj.Transformer.from_crs(32632,f.crs,always_xy=True);x,y=tr.transform(xy[:,0]+293425,xy[:,1]+5499960);c,r=(~f.transform)*(x,y);z=map_coordinates(a,[r-.5,c-.5],order=1)-json.loads((R/'.local_source_cache/r154/terrain.json').read_text())['datum']
(R/'config/r185_dem_heights.json').write_text(json.dumps([[*p,float(h)] for p,h in zip(points,z)]));print(len(points))
