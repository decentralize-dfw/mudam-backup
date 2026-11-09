from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon
D=json.loads((R/'config/r302_fort_surfaces.json').read_text());rows=[]
for r in D['rows']:
 if r['name']=='NORTH_COURT':
  # Retain source-supported original inner court plane; the expanded outline is a visible-source architectural boundary.
  old=next(x for x in json.loads((R/'config/r181_architectural_terraces.json').read_text()) if x['name']=='NORTH_COURT');r['plane']=old['plane'];r['origin']=old['origin'];outer=r['xy'];inner=None
 else:outer=D['eastOuter'];inner=r['xy']
 domain=Polygon(outer);print(r['name'],'valid',domain.is_valid,'area',domain.area)
 assert domain.is_valid
 parts=[domain] if inner is None else [Polygon(inner),domain.difference(Polygon(inner))]
 vs=[];fs=[];lookup={}
 def vi(p):
  key=tuple(round(x,6) for x in p)
  if key not in lookup:
   z=r['plane'][0]*(p[0]-r['origin'][0])+r['plane'][1]*(p[1]-r['origin'][1])+r['plane'][2]
   if inner is not None:
    for i,q in enumerate(outer):
     if sum((a-b)**2 for a,b in zip(p,q))<1e-8:
      study=D['outerHeightStudy'];z=study[i]['median'] if study[i]['n']>=10 else (study[i-1]['median']+study[i+1]['median'])/2
   lookup[key]=len(vs);vs.append([*p,z])
  return lookup[key]
 for part in parts:
  for t in shapely.constrained_delaunay_triangles(part).geoms:
   if t.area>1e-8:fs.append([vi(p) for p in list(t.exterior.coords)[:3]])
 rows.append(dict(name=r['name'],vertices=vs,faces=fs,outline=outer,area=domain.area,source=r,limitations=['Plan boundary traced from rendered source','Eastern tree-occluded bank corner height interpolated between visible neighboring levels'] if inner else ['Bank remnants and inner ruin not yet reconstructed; outer expanded court plane provisional']))
(R/'config/r303_fort_geometry.json').write_text(json.dumps(rows,indent=2))
