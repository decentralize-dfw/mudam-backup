from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely,pyproj
from shapely.geometry import Polygon,LineString,box,Point
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter,maximum_filter
from PIL import Image
D=R/'.local_source_cache/r157';rows=json.loads((D/'terrain_input.json').read_text());p=np.concatenate([r['vertices'] for r in rows]);p=np.unique(np.round(p,6),axis=0);tree=cKDTree(p[:,:2]);ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text());domain=box(-500,-450,650,650)
floors=json.loads((R/'.local_source_cache/r152/site_constraints.json').read_text())['floors'];protect=shapely.union_all([Polygon(f['xy']) for f in floors]).buffer(4);buildings=[];forests=[];paths=[];roads=[];cliffs=[]
for w in ways:
 t=w['tags'];xy=np.asarray(w['xy'])-[293425,5499960]
 if len(xy)<2:continue
 line=LineString(xy)
 if not line.intersects(domain):continue
 if t.get('natural')=='cliff':cliffs.append(line.buffer(3))
 if t.get('highway'):
  pedestrian=t['highway'] in ('path','footway','pedestrian','cycleway','track','steps')
  (paths if pedestrian else roads).append(line.buffer(2 if pedestrian else 4))
 if len(xy)>3 and np.linalg.norm(xy[0]-xy[-1])<.1:
  pol=shapely.make_valid(Polygon(xy)).intersection(domain)
  if t.get('building') or str(w['id']) in ('37847302','26424184'):buildings.append(pol)
  if t.get('natural') in ('wood','scrub') or t.get('landuse')=='forest':forests.append(pol)
buildings=shapely.union_all(buildings+[protect]);forest=shapely.union_all(forests);roads=shapely.union_all(roads);paths=shapely.union_all(paths);cliff=shapely.union_all(cliffs)
protect=protect.union(buildings.buffer(2)).union(cliff)
# Historic walls and bridge contact bands remain fixed.
near=json.loads((R/'.local_source_cache/r152/clean_site.json').read_text())
for m in near['meshes']:
 if m['name'].startswith(('R152_HISTORIC_WALL_','R152_RUIN_','R152_FORT_')):protect=protect.union(shapely.MultiPoint(np.asarray(m['vertices'])[:,:2]).convex_hull.buffer(2))
updates=[]
for row in rows:
 v=np.asarray(row['vertices']);dist,ids=tree.query(v[:,:2],k=64);weights=np.exp(-(dist/4.0)**2);z=(p[ids,2]*weights).sum(1)/weights.sum(1);delta=np.clip(z-v[:,2],-.7,.7);locked=shapely.intersects_xy(protect,v[:,0],v[:,1]);delta[locked]=0;v[:,2]+=delta;centers=np.array([v[f].mean(0) for f in row['faces']]);slots=shapely.contains_xy(roads,centers[:,0],centers[:,1]).astype(int).tolist() if 'ROAD' in row['name'] or 'PATH' in row['name'] else []
 updates.append(dict(name=row['name'],vertices=v.tolist(),material_indices=slots,changed=int((abs(delta)>1e-5).sum()),max_delta=float(abs(delta).max())))
updated=np.concatenate([r['vertices'] for r in updates]);groundtree=cKDTree(updated[:,:2])
def height(xy):
 dist,ids=groundtree.query(np.atleast_2d(xy),k=4);w=1/np.maximum(dist,.05)**3;return (updated[ids,2]*w).sum(1)/w.sum(1)
# One world-sized color field, never repeated. Land-cover boundaries from OSM.
size=2048;rng=np.random.default_rng(157);xx=np.linspace(-500,650,size);yy=np.linspace(650,-450,size);X,Y=np.meshgrid(xx,yy);mask=shapely.contains_xy(forest,X,Y);rock=shapely.contains_xy(cliff,X,Y)
base=np.zeros((size,size,3),np.float32);base[:]=[94,108,68];base[mask]=[67,79,49];base[rock]=[119,116,102]
noise=np.zeros((size,size),np.float32)
for sigma,amp in [(3,1.3),(18,2.8),(65,4.0),(170,3.5)]:
 n=gaussian_filter(rng.normal(size=(size,size)).astype(np.float32),sigma);noise+=n/(n.std()+1e-8)*amp
base+=noise[:,:,None]*[.95,1,.64];base+=rng.normal(0,1.1,base.shape).astype(np.float32);Image.fromarray(np.uint8(np.clip(base,0,255))).save(R/'textures/R157_landcover_atlas.jpg',quality=90)
# Subtle micro-normal; no large blob shapes that read as crumpled ground.
n=gaussian_filter(rng.normal(size=(512,512)),.7);dy,dx=np.gradient(n);normal=np.dstack((-dx*.12,-dy*.12,np.ones_like(n)));normal/=np.linalg.norm(normal,axis=2)[:,:,None];Image.fromarray(np.uint8((normal*.5+.5)*255)).save(R/'textures/R157_ground_micro_normal.png')
# Tree tops detected in the actual classified LiDAR; distribution outside the crop follows woodland polygons.
src=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');q=src['xyz_luref'][src['classification']==5];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(q[:,0],q[:,1]);q=np.column_stack((x-293425,y-5499960,q[:,2]-near['datum']));lo=np.floor(q[:,:2].min(0));ix=np.floor(q[:,:2]-lo).astype(int);shape=ix.max(0)+1;canopy=np.full(shape,-100.);np.maximum.at(canopy,(ix[:,0],ix[:,1]),q[:,2]);maxi=maximum_filter(canopy,size=11);peaks=np.argwhere((canopy==maxi)&(canopy>-50));trees=[];exclude=buildings.buffer(4).union(roads.buffer(1)).union(paths.buffer(.5))
for i,j in peaks:
 xy=lo+[i+.5,j+.5];z=float(height(xy)[0]);h=float(canopy[i,j]-z)
 if h<5 or h>29 or exclude.contains(Point(xy)):continue
 if any(np.linalg.norm(xy-np.array(t['xy']))<6 for t in trees):continue
 trees.append(dict(xy=xy.tolist(),z=z,height=h,radius=min(5.2,max(2,h*.24)),source='LiDAR2024 class5 local canopy maximum',near=True))
near_extent=box(*np.r_[q[:,:2].min(0),q[:,:2].max(0)])
wood=forest.difference(exclude).difference(near_extent)
for x in np.arange(-495,650,15):
 for y in np.arange(-445,650,15):
  xy=np.array([x,y])+rng.uniform(-5,5,2)
  if not wood.contains(Point(xy)):continue
  z=float(height(xy)[0]);h=float(rng.uniform(10,19));trees.append(dict(xy=xy.tolist(),z=z,height=h,radius=float(rng.uniform(3.5,6)),source='OSM woodland extent; representative distribution, not surveyed individual trees',near=False))
(D/'landscape.json').write_text(json.dumps(dict(updates=updates,trees=trees,forest_wkt=forest.wkt,paths_wkt=paths.wkt,roads_wkt=roads.wkt,extent=[-500,-450,650,650],limits=['Building, historic wall and mapped cliff contact zones held fixed.','Terrain height changes capped at 0.7m outside protected zones.','Far woodland tree placement is representative; near peaks follow LiDAR.'])))
print('R157_PREPARED',len(trees),'trees',sum(t['near'] for t in trees),'lidar',flush=True)
