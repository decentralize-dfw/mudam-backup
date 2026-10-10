from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely,rasterio.features
from shapely.geometry import Polygon,shape,mapping
from shapely.affinity import rotate
from scipy.ndimage import median_filter
from scipy.signal import find_peaks
from affine import Affine
D=R/'.local_source_cache/r162';rows=json.loads((R/'config/r161_context_geometry.json').read_text())['buildings'];out=[]
for b in rows:
 a=np.load(D/(b['id']+'.npz'));x,y,z,n=[a[k] for k in ['x','y','z','normal']];xx,yy=np.meshgrid(x,y);angle=float(a['angle']);wx=xx*np.cos(angle)-yy*np.sin(angle);wy=xx*np.sin(angle)+yy*np.cos(angle);poly=Polygon(b['rings'][0]);inside=shapely.contains_xy(poly,wx,wy);valid=inside&np.isfinite(z)&(z>b['base']+2)
 flat=z[valid&(n>.88)];bins=np.arange(np.nanmin(flat)-.2,np.nanmax(flat)+.4,.2);hist,edges=np.histogram(flat,bins);peaks,_=find_peaks(hist,prominence=max(20,len(flat)*.003),distance=4);levels=(edges[peaks]+edges[peaks+1])/2
 if not len(levels):raise RuntimeError('No measured roof modes')
 zz=median_filter(z,size=3);dist=np.abs(zz[:,:,None]-levels);lab=dist.argmin(2).astype('int16')+1;lab[~valid]=0
 # Roof forms are measured segments, not copies of the scan triangles.
 pieces=[]
 for geom,label in rasterio.features.shapes(lab,mask=valid,transform=Affine(.4,0,x[0]-.2,0,.4,y[0]-.2)):
  p=rotate(shape(geom),angle,origin=(0,0),use_radians=True).intersection(poly)
  if p.area<.01:continue
  p=p
  for q in getattr(p,'geoms',[p]):
   if q.geom_type!='Polygon':continue
   pieces.append(dict(z=float(levels[int(label)-1]),polygon=mapping(q)))
 errs=np.abs(z[valid]-levels[lab[valid]-1]);print(b['id'],'levels',levels.tolist(),'parts',len(pieces),'error median/p95',np.quantile(errs,[.5,.95]).tolist())
 out.append(dict(id=b['id'],name=b['name'],base=b['base'],parts=pieces,levels=levels.tolist(),sample_count=int(valid.sum()),roof_sample_error_median=float(np.median(errs)),roof_sample_error_p95=float(np.quantile(errs,.95))))
(D/'roofs.json').write_text(json.dumps(out))
# Triangulate roof polygons; vertical walls stop at measured adjacent roof heights.
verts=[];faces=[]
for b in out:
 polys=[shape(p['polygon']) for p in b['parts']];union=shapely.union_all(polys)
 for p,g in zip(b['parts'],polys):
  z=p['z']
  for t in shapely.constrained_delaunay_triangles(g).geoms:
   v=[(xx,yy,z) for xx,yy in list(t.exterior.coords)[:3]];off=len(verts);verts.extend(v);faces.append([off,off+1,off+2])
  for ring in [g.exterior,*g.interiors]:
   coords=list(ring.coords)
   for aa,bb in zip(coords,coords[1:]):
    # Neighbour test excludes this polygon; keep only exposed vertical span.
    mid=shapely.Point((aa[0]+bb[0])/2,(aa[1]+bb[1])/2);neighbors=[p2['z'] for p2,g2 in zip(b['parts'],polys) if g2 is not g and g2.distance(mid)<.0001];low=max([h for h in neighbors if h<z-.1],default=b['base'])
    if any(h>=z-.1 for h in neighbors):continue
    off=len(verts);verts.extend([(aa[0],aa[1],low),(bb[0],bb[1],low),(bb[0],bb[1],z),(aa[0],aa[1],z)]);faces.append([off,off+1,off+2,off+3])
(D/'mesh.json').write_text(json.dumps(dict(vertices=verts,faces=faces,buildings=out,limitations=['Roof segmentation candidate: 0.4m samples, measured height modes, simplified boundaries.','Source-baked facades do not yet have individually reconstructed window recesses.','Not an exact or complete environment acceptance.'])))
