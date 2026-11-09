"""Interpolate the small cut seam from classified ground outside the source building."""
from pathlib import Path
import json,sys,math
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from shapely.geometry import Polygon,box
from scipy.spatial import cKDTree
from scipy.interpolate import LinearNDInterpolator
fit=json.loads((root/'reports/R151_pavilion_registration_candidate.json').read_text())
old=Polygon(fit['old']);placed=Polygon(np.array(fit['old'])+fit['translation_xy']);source=Polygon(fit['target'])
mask=shapely.from_geojson((root/'.local_source_cache/act_context/architecture_precise_exclusion.geojson').read_text())
domain=mask.intersection(old.union(placed).buffer(3)).difference(placed)
points=np.load(root/'.local_source_cache/act_context/pavilion_ground_points.npz')['xyz'];points=points[~shapely.contains_xy(source.buffer(.3),points[:,0],points[:,1])]
keys=np.floor(points[:,:2]/.25).astype(int);_,idx=np.unique(keys,axis=0,return_index=True);points=points[idx]
interp=LinearNDInterpolator(points[:,:2],points[:,2]);tree=cKDTree(points[:,:2])
def height(xy):
    z=interp(xy);dist,near=tree.query(xy);return np.where(np.isfinite(z),z,points[near,2]),dist
vertices=[];faces=[];indices={}
def vertex(q):
    k=tuple(round(float(x),6) for x in q)
    if k not in indices:indices[k]=len(vertices);vertices.append(k)
    return indices[k]
x0,y0,x1,y1=domain.bounds
for ix in range(math.floor(x0*2),math.ceil(x1*2)):
 for iy in range(math.floor(y0*2),math.ceil(y1*2)):
    part=domain.intersection(box(ix/2,iy/2,(ix+1)/2,(iy+1)/2))
    if part.is_empty or part.area<1e-10:continue
    for tri in shapely.constrained_delaunay_triangles(part).geoms:
        faces.append([vertex(q) for q in list(tri.exterior.coords)[:3]])
xy=np.array(vertices);z,dist=height(xy);samples=[]
for q in np.array(fit['old'])+fit['translation_xy']:
 h,d=height(np.array([q]));samples.append([*q,float(h[0])])
data=dict(accepted=False,vertices=np.column_stack((xy,z)).tolist(),triangles=faces,source_ground_points=points.tolist(),source='ACT classified LiDAR 2024; source-building footprint excluded to avoid interior low returns',domain_area=domain.area,nearest_source_distance_quantiles=np.quantile(dist,[0,.5,.9,1]).tolist(),wall_corner_ground=samples,limits=['Interpolated presentation seam, not a surveyed terrain surface beneath the original building.','Both source height datums are tied to the same road anchor; uncertainty retained.'])
(root/'.local_source_cache/act_context/pavilion_ground_join.json').write_text(json.dumps(data));print(json.dumps({k:v for k,v in data.items() if k not in ['vertices','triangles','source_ground_points']}))
