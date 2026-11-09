from pathlib import Path
import sys,json,numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon
rows=json.loads((R/'config/r303_fort_geometry.json').read_text());row=rows[0];poly=Polygon(row['outline']);a=np.array(row['outline'][0]);b=np.array(row['outline'][1]);u=(b-a)/np.linalg.norm(b-a);normal=np.array([u[1],-u[0]]);bank=poly.intersection(Polygon([a,b,b+normal*4,a+normal*4]));flat=poly.difference(bank);levels=json.loads((R/'config/r304_court_bank_levels.json').read_text())[:4];coef=np.polyfit([np.dot(np.array(v['xy'])-a,u) for v in levels],[v['z'] for v in levels],1);r=row['source'];vs=[];fs=[];lookup={}
for part in [bank,flat]:
 for tri in shapely.constrained_delaunay_triangles(part).geoms:
  ids=[]
  for q in list(tri.exterior.coords)[:3]:
   key=tuple(round(v,6) for v in q)
   if key not in lookup:
    p=np.array(q);z=r['plane'][0]*(p[0]-r['origin'][0])+r['plane'][1]*(p[1]-r['origin'][1])+r['plane'][2];w=max(0,min(1,1-np.dot(p-a,normal)/4));z=z*(1-w)+float(np.polyval(coef,np.dot(p-a,u)))*w;lookup[key]=len(vs);vs.append([*q,z])
   ids.append(lookup[key])
  fs.append(ids)
row['vertices']=vs;row['faces']=fs;row['bankWidthProvisional']=4;row['bankCrestFit']=coef.tolist();row['bankCrestSourceLevels']=levels
(R/'config/r304_court_geometry.json').write_text(json.dumps(row,indent=2));print('Bank',bank.area,'court',poly.area)
