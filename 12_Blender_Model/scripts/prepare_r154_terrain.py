from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely,pyproj,rasterio
from shapely.geometry import Polygon,LineString,box
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.interpolate import LinearNDInterpolator
D=R/'.local_source_cache/r154';D.mkdir(exist_ok=True)
src=json.loads((R/'.local_source_cache/r152/clean_site.json').read_text());constraints=json.loads((R/'.local_source_cache/r152/site_constraints.json').read_text());footprint=shapely.union_all([Polygon(f['xy']) for f in constraints['floors']])
rows=[m for m in src['meshes'] if m['name']=='R152_CLASS2_TERRAIN' or m['name'].startswith(('R152_PATH_','R152_FORECOURT_'))];samples=np.concatenate([m['vertices'] for m in rows]);tree=cKDTree(samples[:,:2]);protect=footprint.buffer(4)
for m in src['meshes']:
 if m['name'].startswith(('R152_HISTORIC_WALL_','R152_RUIN_','R152_FORT_')):protect=protect.union(shapely.MultiPoint(np.asarray(m['vertices'])[:,:2]).convex_hull.buffer(2))
updates=[]
for m in rows:
 v=np.asarray(m['vertices']);dist,ids=tree.query(v[:,:2],k=32);w=np.exp(-(dist/2.8)**2);h=(samples[ids,2]*w).sum(1)/w.sum(1);change=np.clip(h-v[:,2],-.5,.5);lock=shapely.intersects_xy(protect,v[:,0],v[:,1]);change[lock]=0;v[:,2]+=change;updates.append(dict(name=m['name'],vertices=v.tolist(),max_change=float(np.max(np.abs(change))),changed=int((abs(change)>1e-5).sum())))
near_samples=np.concatenate([u['vertices'] for u in updates]);near_tree=cKDTree(near_samples[:,:2]);near=shapely.segmentize(box(-89,-98,98,108),.5)
edge_samples={}
for axis,value in [(0,-89),(0,98),(1,-98),(1,108)]:
 q=near_samples[np.abs(near_samples[:,axis]-value)<1e-5];q=q[np.argsort(q[:,1-axis])];edge_samples[(axis,value)]=(q[:,1-axis],q[:,2])
with rasterio.open(R/'references/terrain_lidar2024/mudam_far_mnt_2024.tif') as f:
 a=f.read(1);transform=f.transform;crs=f.crs
 assert np.isfinite(a).all() and a.min()>0
 a=gaussian_filter(a,2.0)
T=pyproj.Transformer.from_crs(32632,crs,always_xy=True);datum=src['datum']
def height(xy):
 x,y=T.transform(xy[:,0]+293425,xy[:,1]+5499960);c,r=(~transform)*(x,y);z=map_coordinates(a,[r-.5,c-.5],order=1,mode='nearest')-datum
 dx=np.maximum(np.maximum(-89-xy[:,0],xy[:,0]-98),0);dy=np.maximum(np.maximum(-98-xy[:,1],xy[:,1]-108),0);d=np.hypot(dx,dy);dist,ids=near_tree.query(xy,k=4);w=1/np.maximum(dist,.01)**3;edge=(near_samples[ids,2]*w).sum(1)/w.sum(1)
 boundary=np.column_stack((np.clip(xy[:,0],-89,98),np.clip(xy[:,1],-98,108)))
 for (axis,value),(positions,heights) in edge_samples.items():
  selected=np.abs(boundary[:,axis]-value)<1e-5;edge[selected]=np.interp(boundary[selected,1-axis],positions,heights)
 blend=np.clip(d/18,0,1);blend=blend*blend*(3-2*blend);return edge*(1-blend)+z*blend
phila=json.loads((R/'.local_source_cache/r152/philharmonie_clean.json').read_text());domain=box(-500,-450,650,650).difference(near).difference(Polygon(phila['plaza']))
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text());roads=[]
for way in ways:
 t=way['tags'];h=t.get('highway')
 if not h or h in ('steps','construction','proposed') or t.get('bridge')=='yes':continue
 line=LineString(np.asarray(way['xy'])-[293425,5499960])
 if not line.intersects(domain):continue
 try:width=float(t['width'].replace('m',''))
 except (KeyError,ValueError):width=2.6 if h in ('path','footway','pedestrian','cycleway','track') else 7
 roads.append(line.buffer(width/2,cap_style='flat',join_style='round').intersection(domain))
roads=shapely.union_all(roads);meshes=[]
def build(name,poly,material,spacing):
 vs=[];fs=[];lookup={}
 def vi(q):
  key=tuple(np.round(q,6))
  if key not in lookup:lookup[key]=len(vs);vs.append(key)
  return lookup[key]
 x0,y0,x1,y1=poly.bounds
 for x in np.arange(math.floor(x0/spacing)*spacing,x1,spacing):
  for y in np.arange(math.floor(y0/spacing)*spacing,y1,spacing):
   part=poly.intersection(box(x,y,x+spacing,y+spacing))
   if part.is_empty or part.area<1e-7:continue
   for t in shapely.constrained_delaunay_triangles(part).geoms:
    if t.area<1e-7:continue
    fs.append([vi(q) for q in np.asarray(t.exterior.coords)[:3]])
 xy=np.asarray(vs);z=height(xy);meshes.append(dict(name=name,vertices=np.column_stack((xy,z)).tolist(),faces=fs,material=material));print(name,len(vs),len(fs),flush=True)
build('R154_FAR_GROUND',domain.difference(roads),'grass',5)
build('R154_FAR_ROADS',roads,'paving',3)
(D/'terrain.json').write_text(json.dumps(dict(updates=updates,meshes=meshes,extent=[-500,-450,650,650],source='ACT LiDAR2024 MNT',datum=datum,limits=['Near contact/wall zones locked; other near elevations adjusted at most 0.5m to suppress acquisition noise.','Far terrain smoothed over 1m; inherited vertical datum candidate.','Untagged OSM road widths estimated; detailed junction and stair geometry remains separate.'])))
print('R154_TERRAIN_READY',flush=True)
