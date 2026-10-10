from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely,rasterio.features
from shapely.geometry import Polygon,shape,mapping
from shapely.affinity import rotate
from scipy.ndimage import median_filter
from scipy.signal import find_peaks
from affine import Affine
D=R/'.local_source_cache/r164';rows=json.loads((R/'config/r164_building_targets.json').read_text())['buildings'];out=[]
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
# The narrow tower has an inclined roof: fit its measured roof plane,
# rather than flattening the 5m elevation range into a single mode.
for b in out:
 if b['id']!='664452464':continue
 a=np.load(D/(b['id']+'.npz'));xx,yy=np.meshgrid(a['x'],a['y']);ang=float(a['angle']);wx=xx*np.cos(ang)-yy*np.sin(ang);wy=xx*np.sin(ang)+yy*np.cos(ang);poly=Polygon(next(r for r in rows if r['id']==b['id'])['rings'][0]);mask=shapely.contains_xy(poly.buffer(-.8),wx,wy)&np.isfinite(a['z'])&(a['z']>30)&(a['normal']>.6);q=np.column_stack([wx[mask],wy[mask],a['z'][mask]]);A=np.column_stack([q[:,:2],np.ones(len(q))]);rng=np.random.default_rng(164);best=np.zeros(len(q),bool)
 for _ in range(400):
  ids=rng.choice(len(q),3,replace=False)
  if abs(np.linalg.det(A[ids]))<1e-7:continue
  coef=np.linalg.solve(A[ids],q[ids,2]);hit=abs(A@coef-q[:,2])<.3
  if hit.sum()>best.sum():best=hit
 coef=np.linalg.lstsq(A[best],q[best,2],rcond=None)[0];b['roof_plane']=coef.tolist();b['plane_inliers']=int(best.sum());b['plane_samples']=len(q);b['plane_median_error']=float(np.median(abs(A[best]@coef-q[best,2])));print('SLOPED_ROOF',b['roof_plane'],b['plane_inliers'],b['plane_samples'],flush=True)
(D/'roofs.json').write_text(json.dumps(out))
# Node all shared roof boundaries before creating step walls. A midpoint on
# an unsplit long edge can belong to several roof levels and omit wall spans.
verts=[];faces=[];base_vertices=[];stats=[]
for b in out:
 building_vertex_start=len(verts)
 polys=[shape(p['polygon']) for p in b['parts']];tree=shapely.STRtree(polys)
 def level_at(point):
  ids=tree.query(point,predicate='intersects')
  return max((b['parts'][int(i)]['z'] for i in ids),default=b['base'])
 for p,g in zip(b['parts'],polys):
  for t in shapely.constrained_delaunay_triangles(g).geoms:
   tri=list(t.exterior.coords)[:3];cross=(tri[1][0]-tri[0][0])*(tri[2][1]-tri[0][1])-(tri[1][1]-tri[0][1])*(tri[2][0]-tri[0][0]);tri=tri if cross>0 else tri[::-1];off=len(verts);verts.extend([(xx,yy,p['z']) for xx,yy in tri]);faces.append([off,off+1,off+2])
 lines=shapely.union_all([p.boundary for p in polys]);wall_count=0
 for line in getattr(lines,'geoms',[lines]):
  coords=list(line.coords)
  for aa,bb in zip(coords,coords[1:]):
   aa=np.array(aa);bb=np.array(bb);delta=bb-aa;length=np.linalg.norm(delta)
   if length<1e-5:continue
   mid=(aa+bb)/2;left=np.array([-delta[1],delta[0]])/length*.0001
   hl=level_at(shapely.Point(mid+left));hr=level_at(shapely.Point(mid-left))
   if abs(hl-hr)<.001:continue
   lo,hi=sorted([hl,hr]);off=len(verts)
   verts.extend([(aa[0],aa[1],lo),(bb[0],bb[1],lo),(bb[0],bb[1],hi),(aa[0],aa[1],hi)])
   faces.append([off,off+1,off+2,off+3] if hl>hr else [off+3,off+2,off+1,off])
   if abs(lo-b['base'])<.001:base_vertices.extend([off,off+1])
   wall_count+=1
 if 'roof_plane' in b:
  for v in verts[building_vertex_start:]:
   if v[2]>b['base']+.01:
    pass
  for i in range(building_vertex_start,len(verts)):
   x,y,z=verts[i]
   if z>b['base']+.01:verts[i]=(x,y,float(np.dot([x,y,1],b['roof_plane'])))
 stats.append(dict(id=b['id'],wall_spans=wall_count))
(D/'mesh.json').write_text(json.dumps(dict(vertices=verts,faces=faces,base_vertices=base_vertices,buildings=out,wall_stats=stats,limitations=['0.4m building-axis roof sampling and measured height modes; approximate envelope.','Source-baked facade color; window recesses not independently reconstructed.','Not exact or complete environment acceptance.'])))
print('NODED_WALLS',stats,flush=True)
