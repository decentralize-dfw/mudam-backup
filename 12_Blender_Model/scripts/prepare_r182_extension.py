from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely,rasterio,pyproj
from shapely.geometry import box,LineString
from scipy.ndimage import gaussian_filter,map_coordinates
with rasterio.open(R/'references/terrain_lidar2024/mudam_extended_mnt_2024.tif') as f:
 a=gaussian_filter(f.read(1),2);transform=f.transform;crs=f.crs
T=pyproj.Transformer.from_crs(32632,crs,always_xy=True)
def height(xy):
 x,y=T.transform(xy[:,0]+293425,xy[:,1]+5499960);c,r=(~transform)*(x,y)
 assert np.all((r>=-.51)&(c>=-.51)&(r<a.shape[0]+.51)&(c<a.shape[1]+.51)), (r.min(),c.min(),r.max(),c.max(),a.shape)
 return map_coordinates(a,[r-.5,c-.5],order=1,mode='nearest')-json.loads((R/'.local_source_cache/r154/terrain.json').read_text())['datum']
domain=box(-600,-600,800,800).difference(box(-500,-450,650,650))
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text(encoding='utf8'));merged={str(w['id']):w for w in ways}
for w in json.loads((R/'config/r177_merged_road_sources.json').read_text()):merged[str(w['id'])]=w
roads=[]
for w in merged.values():
 t=w['tags'];h=t.get('highway')
 if h not in ['secondary','tertiary','residential','service','footway','path','pedestrian','cycleway','track'] or t.get('bridge') in ['yes','viaduct'] or t.get('tunnel')=='yes':continue
 line=LineString(np.array(w['xy'])-[293425,5499960])
 if not line.intersects(domain):continue
 try:width=float(t['width'].replace('m',''))
 except:width=2.6 if h in ['footway','path','pedestrian','cycleway','track'] else 6.5
 roads.append(line.buffer(width/2,cap_style='flat',join_style='round').intersection(domain))
roads=shapely.union_all(roads);meshes=[]
for name,g in [('GROUND',domain.difference(roads)),('ROADS',roads)]:
 vs=[];fs=[];lookup={}
 def vi(p):
  k=tuple(round(float(v),6) for v in p)
  if k not in lookup:lookup[k]=len(vs);vs.append(k)
  return lookup[k]
 for x in range(-600,800,5):
  for y in range(-600,800,5):
   if -500<=x<650 and -450<=y<650:continue
   cell=g.intersection(box(x,y,x+5,y+5))
   if cell.is_empty:continue
   for t in shapely.constrained_delaunay_triangles(cell).geoms:
    if t.area>1e-8:fs.append([vi(p) for p in list(t.exterior.coords)[:3]])
 xy=np.array(vs);z=height(xy);meshes.append(dict(name=name,vertices=np.c_[xy,z].tolist(),faces=fs));print(name,len(vs),len(fs),flush=True)
(R/'config/r182_extension_meshes.json').write_text(json.dumps(dict(meshes=meshes,source='ACT LiDAR2024 MNT 0.5m; 1m Gaussian smoothing; 5m authored terrain tessellation',extent=[-600,-600,800,800],limits=['Road widths without tags are provisional','Only exterior ring; current museum and internal terrain untouched'])))
