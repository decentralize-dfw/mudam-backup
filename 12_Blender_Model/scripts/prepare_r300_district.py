from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,rasterio,pyproj,shapely
from shapely.geometry import Polygon,box
from scipy.ndimage import gaussian_filter,map_coordinates
missing=json.loads((R/'reports/R299_DISTRICT_COVERAGE.json').read_text())['missing'];preserved={'164179202','1337806219','1337806220','1337806221'}
with rasterio.open(R/'references/terrain_lidar2024/mudam_extended_mnt_2024.tif') as f:
 grid=gaussian_filter(f.read(1),2);transform=f.transform;crs=f.crs
T=pyproj.Transformer.from_crs(32632,crs,always_xy=True);datum=json.loads((R/'.local_source_cache/r154/terrain.json').read_text())['datum']
def height(xy):
 xy=np.array(xy);x,y=T.transform(xy[:,0]+293425,xy[:,1]+5499960);c,r=(~transform)*(x,y)
 assert np.all((r>=0)&(c>=0)&(r<grid.shape[0])&(c<grid.shape[1]))
 return map_coordinates(grid,[r-.5,c-.5],order=1,mode='nearest')-datum
points=np.load(R/'.local_source_cache/r171/lower_reference.npz')['xyz'];buildings=[]
for w in missing:
 if str(w['id']) in preserved:continue
 p=w['polygon'];p=p[:-1] if np.linalg.norm(np.array(p[0])-p[-1])<1e-6 else p;g=Polygon(p);lo=np.min(p,axis=0);hi=np.max(p,axis=0)
 sub=points[(points[:,0]>=lo[0])&(points[:,0]<=hi[0])&(points[:,1]>=lo[1])&(points[:,1]<=hi[1])];sub=sub[shapely.contains_xy(g,sub[:,0],sub[:,1])]
 edge=[]
 for a,b in zip(p,p[1:]+p[:1]):
  a=np.array(a);b=np.array(b);edge.extend(a+(b-a)*t for t in np.linspace(0,1,max(2,math.ceil(np.linalg.norm(b-a)/.5))))
 z=height(edge);base=float(min(z)-.2);top=float(np.quantile(sub[:,2],.85)) if len(sub)>=12 else None;basis='ACT scalar roof estimate p85'
 if top is None or top<max(z)+2 or top-base>35:
  tags=w['tags'];h=float(tags['height'].replace('m','')) if 'height' in tags else float(tags.get('building:levels',2.5))*3.2;top=float(max(z)+h);basis='OSM height' if 'height' in tags else 'Provisional levels x3.2m; unknown default8m, user-authorized abstract mass'
 buildings.append(dict(id=w['id'],polygon=p,base=base,top=top,heightBasis=basis,sourceSamples=len(sub)))
outside=shapely.union_all([Polygon(b['polygon']).buffer(3,join_style='mitre') for b in buildings]).difference(box(-600,-600,800,800));vs=[];fs=[];lookup={}
def vi(p):
 key=tuple(round(float(v),6) for v in p)
 if key not in lookup:lookup[key]=len(vs);vs.append(key)
 return lookup[key]
if not outside.is_empty:
 xmin,ymin,xmax,ymax=outside.bounds
 for x in range(math.floor(xmin),math.ceil(xmax)):
  for y in range(math.floor(ymin),math.ceil(ymax)):
   cell=outside.intersection(box(x,y,x+1,y+1))
   if cell.is_empty:continue
   for t in shapely.constrained_delaunay_triangles(cell).geoms:
    if t.area>1e-9:fs.append([vi(q) for q in list(t.exterior.coords)[:3]])
z=height(vs) if vs else [];terrain=dict(vertices=[[x,y,float(h)] for (x,y),h in zip(vs,z)],faces=fs)
(R/'config/r300_district_completion.json').write_text(json.dumps(dict(buildings=buildings,preservedDetailedRowIds=sorted(preserved),terrainExtension=terrain,terrainSource='Existing ACT LiDAR2024 MNT, same smoothing/datum as R182; 1m triangulation only outside current terrain domain'),indent=2));print('New masses',len(buildings),'extension faces',len(fs),flush=True)
