from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import triangulate
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter1d
D=R/'.local_source_cache/r154';old=json.loads((R/'.local_source_cache/r152/clean_site.json').read_text());row=next(m for m in old['meshes'] if m['name']=='R152_FORT_THUNGEN_WALLS');v=np.asarray(row['vertices']);n=len(v)//2;fp=Polygon(v[:n,:2]);act=np.load(R/'.local_source_cache/r152/site_reference_points.npz')['xyz'];at=cKDTree(act[:,:2]);ground=np.load(R/'.local_source_cache/r152/ground_samples.npz')['xyz'];gt=cKDTree(ground[:,:2])
def ortho(px):
 q=np.asarray(px);return np.column_stack((-48+(q[:,0]-700)/14,-40-(q[:,1]-700)/14))
def triangles(poly):return [list(t.exterior.coords)[:3] for t in triangulate(poly) if poly.covers(t)]
# Use the mapped footprint, keeping its rounded tower bases in the main mass.
outline=np.asarray(fp.exterior.coords)[:-1];dist,ids=gt.query(outline,k=8);bases=ground[ids,2].min(1)-.3
metal=Polygon(ortho([(483,806),(550,854),(648,737),(757,635),(857,558),(918,550),(972,564),(1027,595),(1070,556),(1086,379),(1037,333),(877,327),(829,371),(848,427),(830,492),(778,555),(688,645),(585,741)]))
roof=fp.difference(metal)
# A refined surface follows low-vegetation fort roof samples, not canopy points.
pts=act[(act[:,2]>1.8)&(act[:,2]<4.5)];rt=cKDTree(pts[:,:2]);roofvs=[];rooffs=[];lookup={}
for x in np.arange(fp.bounds[0],fp.bounds[2],1):
 for y in np.arange(fp.bounds[1],fp.bounds[3],1):
  part=roof.intersection(shapely.box(x,y,x+1,y+1))
  if part.area<1e-7:continue
  for t in shapely.constrained_delaunay_triangles(part).geoms:
   if t.area<1e-7:continue
   face=[]
   for q in list(t.exterior.coords)[:3]:
    key=tuple(np.round(q,6))
    if key not in lookup:lookup[key]=len(roofvs);roofvs.append(key)
    face.append(lookup[key])
   rooffs.append(face)
xy=np.asarray(roofvs);d,ids=rt.query(xy,k=32);z=np.median(pts[ids,2],axis=1);z=np.clip(z,2.9,4.2)
# Entrance bridge meets the front wall at the source-traced path intersection.
ab=ortho([(257,1038),(450,887)]);line=LineString([ab[0],ab[1]+(ab[1]-ab[0])*.4]);hit=line.intersection(fp.boundary)
if hit.geom_type=='MultiPoint':entry=min(hit.geoms,key=lambda p:p.distance(Point(ab[0])))
else:entry=hit
if entry.is_empty:raise RuntimeError('Bridge trace must intersect fort footprint')
entry=np.array(entry.coords[0]);direction=(ab[1]-ab[0]);direction/=np.linalg.norm(direction);tangent=np.array([direction[1],-direction[0]])
source=next(m for m in old['meshes'] if m['name']=='R152_FORT_ENTRANCE_BRIDGE');deck=np.asarray(source['vertices']);deck_z=float(np.median(deck[:,2]));start=ab[0];end=entry+direction*.3
result=dict(footprint=outline.tolist(),bases=bases.tolist(),body_top=2.9,cap_triangles=triangles(fp),roof_vertices=np.column_stack((xy,z)).tolist(),roof_faces=rooffs,metal_triangles=triangles(metal),metal_outline=list(metal.exterior.coords)[:-1],towers=old['towers'],entry=entry.tolist(),direction=direction.tolist(),tangent=tangent.tolist(),deck_start=start.tolist(),deck_end=end.tolist(),deck_z=deck_z,limits=['Fort footprint from OSM; portal positions follow ACT bridge trace.','Opening widths, cornice offsets and acorn profiles are visual reconstruction candidates, not measured details.','Roof samples restricted to 1.8-4.5m to reject tree canopies.'])
(D/'fort.json').write_text(json.dumps(result));print('FORT_READY',entry,deck_z,flush=True)

