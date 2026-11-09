"""Prepare two existing moat footprints from official 0.5 m DTM; no architectural edits."""
from pathlib import Path
import sys,json,hashlib,math
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'.local_source_cache/gis_runtime'))
import numpy as np,rasterio,pyproj,shapely
from shapely.geometry import Polygon,box
from shapely.ops import orient
src=B/'references/terrain_lidar2024/mudam_mnt_2024_crop.tif';manifest=json.loads(src.with_name('manifest.json').read_text(encoding='utf8'));assert hashlib.sha256(src.read_bytes()).hexdigest()==manifest['sha256']
T=pyproj.Transformer.from_crs(32632,2169,always_xy=True)
with rasterio.open(src) as ds:
 a=ds.read(1);inv=~ds.transform
 def height(x,y):
  e,n=T.transform(293425+x,5499960+y);c,r=inv*(e,n);c-=.5;r-=.5;i,j=math.floor(c),math.floor(r);assert 0<=i<a.shape[1]-1 and 0<=j<a.shape[0]-1
  u,v=c-i,r-j;return float((1-u)*(1-v)*a[j,i]+u*(1-v)*a[j,i+1]+(1-u)*v*a[j+1,i]+u*v*a[j+1,i+1])
 # Existing approach road beyond bridge end. This is a model datum tie, not surveyed building level.
 anchors=[(x,y) for x in [27,29,31,33] for y in [69,71,73]];zs=[height(x,y) for x,y in anchors];datum=float(np.median(zs));results=[]
 for name,filename,key in [('R35_MOAT_GROUND','site_moat.json','moat_polygon'),('R68_MOAT_GROUND','pavilion_moat.json','polygon')]:
  p=orient(Polygon(json.loads((B/'config'/filename).read_text())[key]),sign=1);assert p.is_valid
  vs=[];faces=[];index={}
  def vertex(q):
   key=tuple(round(float(t),6) for t in q[:2])
   if key not in index:index[key]=len(vs);vs.append([*key,height(*key)-datum])
   return index[key]
  x0,y0,x1,y1=p.bounds
  for x in range(math.floor(x0),math.ceil(x1)):
   for y in range(math.floor(y0),math.ceil(y1)):
    q=p.intersection(box(x,y,x+1,y+1))
    if q.is_empty or q.area<1e-9:continue
    for tri in shapely.constrained_delaunay_triangles(q).geoms:
     tri=orient(tri,sign=1);f=[vertex(pt) for pt in list(tri.exterior.coords)[:3]]
     if len(set(f))==3:faces.append(f)
  edges={}
  for f in faces:
   for i,j in zip(f,f[1:]+f[:1]):
    k=tuple(sorted((i,j)));edges.setdefault(k,[]).append((i,j))
  assert all(len(v)<=2 for v in edges.values());boundary=[v[0] for v in edges.values() if len(v)==1]
  results.append(dict(name=name,vertices=vs,triangles=faces,boundary_edges=boundary,footprint_area_m2=p.area,z_min=min(v[2] for v in vs),z_max=max(v[2] for v in vs)))
 receipt=dict(source=src.relative_to(B.parent).as_posix(),source_sha256=manifest['sha256'],grid_spacing_m=1,source_resolution_m=.5,datum_national_m=datum,datum_method='Median DTM at 12 existing approach-road points mapped to scene z=0; conditional building tie',datum_anchors=[dict(x=x,y=y,national_z=z) for (x,y),z in zip(anchors,zs)],datum_spread_m=max(zs)-min(zs),crs='EPSG:2169 -> EPSG:32632',surfaces=results,construction_acceptance=False)
 (B/'.local_source_cache/r150_terrain_mesh.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({k:v for k,v in receipt.items() if k!='surfaces'},indent=2))
 for r in results:print(r['name'],len(r['vertices']),len(r['triangles']),r['footprint_area_m2'],r['z_min'],r['z_max'])
