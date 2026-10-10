from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from scipy.ndimage import median_filter
from shapely.geometry import Polygon
D=R/'.local_source_cache/r167';rows=json.loads((R/'config/r167_building_targets.json').read_text())['buildings'];verts=[];faces=[];base_vertices=[];stats=[]
for b in rows:
 a=np.load(D/(b['id']+'.npz'));xx,yy=np.meshgrid(a['x'],a['y']);ang=float(a['angle']);wx=xx*np.cos(ang)-yy*np.sin(ang);wy=xx*np.sin(ang)+yy*np.cos(ang);z=median_filter(a['z'],size=3);p=Polygon(b['rings'][0]);valid=shapely.contains_xy(p,wx,wy)&np.isfinite(z)&(z>b['base']+2);ids={};edges={};first=len(faces)
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
 count=len(faces)-first;walls=0
 for e in edges.values():
  if len(e)!=1:continue
  aa,bb=e[0];va,vb=verts[aa],verts[bb];off=len(verts);verts.extend([(va[0],va[1],b['base']),(vb[0],vb[1],b['base'])]);faces.append([aa,off,off+1,bb]);base_vertices.extend([off,off+1]);walls+=1
 if count<10:raise RuntimeError('Insufficient roof source '+b['id'])
 stats.append(dict(id=b['id'],name=b['name'],roof_quads=count,wall_spans=walls,roof_min=float(z[valid].min()),roof_max=float(z[valid].max())));print(stats[-1])
(D/'mesh.json').write_text(json.dumps(dict(vertices=verts,faces=faces,base_vertices=base_vertices,wall_stats=stats,limitations=['OSM footprints and ACT2020 0.4m sampled roofs; source dates differ.','Median-filtered measured roof slopes retained; facade relief not reconstructed.','Raster footprint edges and source vegetation occlusion remain approximate.'])))
