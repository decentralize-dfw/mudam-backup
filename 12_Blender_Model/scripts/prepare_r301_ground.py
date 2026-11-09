from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely,numpy as np,rasterio,pyproj
from shapely.geometry import Polygon,box
from scipy.ndimage import gaussian_filter,map_coordinates
D=json.loads((R/'config/r301_ground_domains.json').read_text());polys=[];segments=[]
for t in D['triangles']:
 p=np.array(t['points']);g=Polygon(p[:,:2])
 if g.area<1e-9:continue
 polys.append(g)
 for a,b in zip(p,np.roll(p,-1,axis=0)):segments.append((a,b))
cover=shapely.union_all(polys);domains=[Polygon([p[:2] for p in d['ring']]).buffer(0).buffer(.5) for d in D['domains']];gap=shapely.union_all(domains).difference(cover)
with rasterio.open(R/'references/terrain_lidar2024/mudam_extended_mnt_2024.tif') as f:grid=gaussian_filter(f.read(1),2);tr=f.transform;crs=f.crs
T=pyproj.Transformer.from_crs(32632,crs,always_xy=True);datum=json.loads((R/'.local_source_cache/r154/terrain.json').read_text())['datum']
a=np.array([s[0] for s in segments]);b=np.array([s[1] for s in segments]);ab=b-a;den=np.sum(ab[:,:2]**2,axis=1);den=np.maximum(den,1e-20)
verts=[];faces=[];lookup={};maxblend=0
for domain in [shapely.union_all(domains)]:
 g=domain.difference(cover)
 if g.is_empty:continue
 xmin,ymin,xmax,ymax=g.bounds
 for x in range(math.floor(xmin),math.ceil(xmax)):
  for y in range(math.floor(ymin),math.ceil(ymax)):
   cell=g.intersection(box(x,y,x+1,y+1))
   if cell.is_empty:continue
   for tri in shapely.constrained_delaunay_triangles(cell).geoms:
    if tri.area<1e-8:continue
    ids=[]
    for p in list(tri.exterior.coords)[:3]:
     key=tuple(round(v,7) for v in p)
     if key not in lookup:
      q=np.array(p);t=np.clip(np.sum((q-a[:,:2])*ab[:,:2],axis=1)/den,0,1);near=a+ab*t[:,None];dist=np.linalg.norm(near[:,:2]-q,axis=1);i=np.argmin(dist);zedge=near[i,2]
      xx,yy=T.transform(p[0]+293425,p[1]+5499960);cc,rr=(~tr)*(xx,yy);zdem=float(map_coordinates(grid,[[rr-.5],[cc-.5]],order=1)[0]-datum);blend=min(1,float(dist[i])/2);z=zedge*(1-blend)+zdem*blend
      lookup[key]=len(verts);verts.append([*p,z])
     ids.append(lookup[key])
    faces.append(ids)
# Domains overlap; eliminate identical faces.
faces=list({tuple(sorted(f)):f for f in faces}.values())
(R/'config/r301_ground_patch.json').write_text(json.dumps(dict(vertices=verts,faces=faces,area=gap.area,waterExcluded=True,basis='Current ground and water triangle coverage difference; boundary heights preserved, interior blended to cached ACT LiDAR2024 MNT',domains=D['domains']),indent=2));print(len(verts),len(faces),gap.area)

