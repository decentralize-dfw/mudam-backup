from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from scipy.ndimage import median_filter,distance_transform_edt
from scipy.interpolate import RegularGridInterpolator
from shapely.geometry import Polygon,box
from shapely.affinity import rotate
D=R/'.local_source_cache/r169';rows=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'];verts=[];faces=[];base_vertices=[];stats=[]
for b in rows:
 a=np.load(D/(b['id']+'.npz'));x,y=a['x'],a['y'];ang=float(a['angle']);p=Polygon(b['rings'][0]);pl=rotate(p,-ang,origin=(0,0),use_radians=True);z=median_filter(a['z'],size=3);valid=np.isfinite(z)&(z>b['base']+2);nearest=distance_transform_edt(~valid,return_distances=False,return_indices=True);filled=z[tuple(nearest)];interp=RegularGridInterpolator((y,x),filled,bounds_error=True);ids={};edges={};first=len(faces);pieces=[]
 def vertex(q):
  xx,yy=q;wx=xx*np.cos(ang)-yy*np.sin(ang);wy=xx*np.sin(ang)+yy*np.cos(ang);key=(round(wx,7),round(wy,7))
  if key not in ids:ids[key]=len(verts);verts.append((wx,wy,float(interp([[yy,xx]])[0])))
  return ids[key]
 for j in range(len(y)-1):
  for i in range(len(x)-1):
   g=box(x[i],y[j],x[i+1],y[j+1]).intersection(pl)
   if g.is_empty or g.area<1e-10:continue
   for q in getattr(g,'geoms',[g]):
    if q.geom_type!='Polygon':continue
    q=shapely.orient_polygons(q);pieces.append(q)
    for t in shapely.constrained_delaunay_triangles(q).geoms:
     t=shapely.orient_polygons(t);f=[vertex(v) for v in list(t.exterior.coords)[:3]];faces.append(f)
     for aa,bb in zip(f,f[1:]+f[:1]):
      key=tuple(sorted((aa,bb)));edges[key]=edges.get(key,[])+[(aa,bb)]
 roof_count=len(faces)-first;walls=0
 for e in edges.values():
  if len(e)!=1:continue
  aa,bb=e[0];va,vb=verts[aa],verts[bb];off=len(verts);verts.extend([(va[0],va[1],b['base']),(vb[0],vb[1],b['base'])]);faces.append([aa,off,off+1,bb]);base_vertices.extend([off,off+1]);walls+=1
 coverage=shapely.union_all(pieces);missing=pl.difference(coverage).area
 assert missing<1e-5,(b['id'],missing)
 stats.append(dict(id=b['id'],roof_triangles=roof_count,wall_spans=walls,footprint_uncovered_m2=missing,footprint_area_m2=p.area));print(stats[-1])
(D/'mesh.json').write_text(json.dumps(dict(vertices=verts,faces=faces,base_vertices=base_vertices,wall_stats=stats,limitations=['Clipped grid covers exact OSM outline; OSM/ACT survey alignment not guaranteed.','Roof interpolation from 0.4m ACT samples; missing edge samples use nearest valid roof sample.','Separate party-wall surfaces and fine facade relief remain unresolved.'])))
