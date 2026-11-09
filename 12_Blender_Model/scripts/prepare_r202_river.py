from pathlib import Path
import sys,json,numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely,rasterio,pyproj
from shapely.geometry import Polygon,box,Point
from scipy.ndimage import map_coordinates
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text());parts=[]
for row in ways:
 if row['tags'].get('natural')!='water' or row['tags'].get('water')!='river':continue
 p=Polygon(np.array(row['xy'])-[293425,5499960]);p=shapely.make_valid(p).intersection(box(-500,-450,650,650))
 if not p.is_empty:parts.append(p)
g=shapely.union_all(parts);polys=list(g.geoms) if hasattr(g,'geoms') else [g]
with rasterio.open(R/'references/terrain_lidar2024/mudam_extended_mnt_2024.tif') as f:a=f.read(1);tr=f.transform;crs=f.crs
T=pyproj.Transformer.from_crs(32632,crs,always_xy=True);out=[]
for p in polys:
 if p.geom_type!='Polygon' or p.area<10:continue
 vs=[];faces=[];lookup={}
 def vi(v):
  k=tuple(round(float(x),6) for x in v)
  if k not in lookup:lookup[k]=len(vs);vs.append(k)
  return lookup[k]
 lo,bo,hi,to=p.bounds
 for x in np.arange(np.floor(lo/4)*4,hi,4):
  for y in np.arange(np.floor(bo/4)*4,to,4):
   for t in shapely.constrained_delaunay_triangles(p.intersection(box(x,y,x+4,y+4))).geoms:
    if t.area>1e-7:faces.append([vi(v) for v in list(t.exterior.coords)[:3]])
 xy=np.array(vs);xx,yy=T.transform(xy[:,0]+293425,xy[:,1]+5499960);cc,rr=(~tr)*(xx,yy);z=map_coordinates(a,[rr-.5,cc-.5],order=1,mode='nearest')-316.1510257594697
 # Fit only interior water observations, excluding bank vertices.
 m=np.array([p.boundary.distance(Point(*v))>1.5 for v in xy]);origin=xy.mean(0);X=np.c_[xy-origin,np.ones(len(xy))];c=np.linalg.lstsq(X[m],z[m],rcond=None)[0]
 for _ in range(5):
  err=abs(X@c-z);mask=m&(err<.5)
  if mask.sum()<10:break
  c=np.linalg.lstsq(X[mask],z[mask],rcond=None)[0]
 out.append(dict(area=p.area,outer=list(p.exterior.coords)[:-1],holes=[list(r.coords)[:-1] for r in p.interiors],vertices=np.c_[xy,X@c].tolist(),faces=faces,plane=c.tolist(),origin=origin.tolist(),source_fit_samples=int(mask.sum()),p90=float(np.quantile(abs(X[mask]@c-z[mask]),.9)),totalSamples=int(m.sum())))
(R/'config/r202_river_domains.json').write_text(json.dumps(dict(accepted=False,sourceWays=['76345435','547913332'],source='OSM river banks and ACT2024 MNT; independent planar water surface',domains=out)))
print([(d['area'],d['plane'],d['p90'],d['source_fit_samples'],d['totalSamples']) for d in out])
