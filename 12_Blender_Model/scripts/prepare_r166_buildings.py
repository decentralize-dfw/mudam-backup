from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely,rasterio.features
from shapely.geometry import Polygon,shape,mapping
from shapely.affinity import rotate
from scipy.ndimage import median_filter
from scipy.signal import find_peaks
from affine import Affine
D=R/'.local_source_cache/r166';rows=json.loads((R/'config/r166_building_targets.json').read_text())['buildings'];out=[]
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
# Node all shared roof boundaries before creating step walls. A midpoint on
# an unsplit long edge can belong to several roof levels and omit wall spans.
verts=[];faces=[];base_vertices=[];stats=[]
for b in out:
 if b['id']=='oval_glass_roof':
  a=np.load(D/(b['id']+'.npz'));xx,yy=np.meshgrid(a['x'],a['y']);ang=float(a['angle']);wx=xx*np.cos(ang)-yy*np.sin(ang);wy=xx*np.sin(ang)+yy*np.cos(ang);z=median_filter(a['z'],size=3);poly=Polygon(next(r for r in rows if r['id']==b['id'])['rings'][0]);valid=shapely.contains_xy(poly,wx,wy)&np.isfinite(z)&(z>b['base']+2)
  ids={};edges={};start=len(faces)
  def vertex(j,i):
   key=(j,i)
   if key not in ids:ids[key]=len(verts);verts.append((float(wx[j,i]),float(wy[j,i]),float(z[j,i])))
   return ids[key]
  for j in range(z.shape[0]-1):
   for i in range(z.shape[1]-1):
    if not valid[j:j+2,i:i+2].all():continue
    f=[vertex(j,i),vertex(j,i+1),vertex(j+1,i+1),vertex(j+1,i)];faces.append(f)
    for aa,bb in zip(f,f[1:]+f[:1]):
     key=tuple(sorted((aa,bb)));edges[key]=edges.get(key,[])+[(aa,bb)]
  wall_count=0
  for e in edges.values():
   if len(e)!=1:continue
   aa,bb=e[0];va,vb=verts[aa],verts[bb];off=len(verts);verts.extend([(va[0],va[1],b['base']),(vb[0],vb[1],b['base'])]);faces.append([aa,off,off+1,bb]);base_vertices.extend([off,off+1]);wall_count+=1
  b['surface_method']='0.4m sampled roof surface with median filter; retains curved glass roof rather than flattening it';stats.append(dict(id=b['id'],wall_spans=wall_count,roof_quads=len(faces)-start-wall_count));continue
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
 stats.append(dict(id=b['id'],wall_spans=wall_count))
(D/'mesh.json').write_text(json.dumps(dict(vertices=verts,faces=faces,base_vertices=base_vertices,buildings=out,wall_stats=stats,limitations=['0.4m building-axis roof sampling and measured height modes; approximate envelope.','Source-baked facade color; window recesses not independently reconstructed.','Not exact or complete environment acceptance.'])))
print('NODED_WALLS',stats,flush=True)
