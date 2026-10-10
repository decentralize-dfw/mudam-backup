from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from shapely.geometry import Polygon,LineString,box
from scipy.spatial import cKDTree
D=R/'.local_source_cache/r161';surfaces=json.loads((D/'surfaces.json').read_text());ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text(encoding='utf-8'))
domain=box(-495,-445,645,645);existing=[];allbuildings=[];desired=[];exclusions=[]
for row in surfaces:
 if 'PATH' in row['name'] or 'ROAD' in row['name'] or 'FORECOURT' in row['name']:
  v=np.array(row['vertices']);existing.extend(Polygon(v[f,:2]) for f in row['faces'] if Polygon(v[f,:2]).area>1e-7)
existing=shapely.union_all(existing)
for w in ways:
 xy=np.array(w['xy'])-[293425,5499960];t=w['tags']
 if len(xy)>3 and np.linalg.norm(xy[0]-xy[-1])<.05 and (t.get('building') or t.get('building:part')):allbuildings.append(shapely.make_valid(Polygon(xy)))
 h=t.get('highway')
 if not h or len(xy)<2:continue
 line=LineString(xy)
 if h in ('steps','construction','proposed') or t.get('bridge')=='yes' or t.get('tunnel')=='yes':exclusions.append(line.buffer(5));continue
 if not line.intersects(domain):continue
 try:width=float(t['width'].replace('m',''))
 except (KeyError,ValueError):width=2.6 if h in ('path','footway','pedestrian','cycleway','track') else 7
 desired.append(line.buffer(width/2,cap_style='round',join_style='round'))
protect=shapely.union_all(allbuildings).buffer(.25).union(shapely.union_all(exclusions))
# Keep museum, moat and retained bridge connections untouched.
plaza=json.loads((R/'.local_source_cache/r152/philharmonie_clean.json').read_text())['plaza']
protect=protect.union(box(-90,-100,100,110)).union(Polygon(plaza).buffer(.05))
missing=shapely.make_valid(shapely.union_all(desired).intersection(domain).difference(protect).difference(existing.buffer(.015)))
parts=[p for p in getattr(missing,'geoms',[missing]) if p.area>.08]
missing=shapely.union_all(parts);triangles=[]
for p in parts:
 x0,y0,x1,y1=p.bounds
 for x in np.arange(math.floor(x0/3)*3,x1,3):
  for y in np.arange(math.floor(y0/3)*3,y1,3):
   piece=p.intersection(box(x,y,x+3,y+3))
   if piece.area<1e-7:continue
   triangles.extend([list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(piece).geoms if t.area>1e-7])
# Match the terrain's actual triangles so added paths cannot cut underneath it.
ground_triangles=[]
for row in surfaces:
 if row['name'] not in ('R152_CLASS2_TERRAIN','R154_FAR_GROUND'):continue
 v=np.array(row['vertices'])
 for f in row['faces']:
  xyz=v[f];p=Polygon(xyz[:,:2])
  if p.area<1e-8 or not p.intersects(missing):continue
  piece=p.intersection(missing)
  if piece.area<1e-8:continue
  coeff=np.linalg.solve(np.column_stack((xyz[:,:2],np.ones(3))),xyz[:,2])
  for tri in shapely.constrained_delaunay_triangles(piece).geoms:
   if tri.area<1e-8:continue
   ground_triangles.append([[x,y,float(np.dot([x,y,1],coeff))+.018] for x,y in list(tri.exterior.coords)[:3]])
triangles=ground_triangles
points=np.load(D/'reference.npz')['xyz'];buildings=[]
for ident,levels in [('24457411',5),('24457477',3)]:
 w=next(w for w in ways if str(w['id'])==ident);poly=shapely.orient_polygons(Polygon(np.array(w['xy'])-[293425,5499960]));inside=points[shapely.contains_xy(poly.buffer(-2),points[:,0],points[:,1])]
 roof=float(np.quantile(inside[:,2],.82));base=roof-float(w['tags']['height'])
 buildings.append(dict(id=ident,name=w['tags']['name'],rings=[list(poly.exterior.coords)[:-1]],roof=roof,base=base,levels=levels,height_tag=float(w['tags']['height']),roof_triangles=[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(poly).geoms]))
for b in buildings:
 poly=Polygon(b['rings'][0]);b['tiers']=[]
 for i in range(b['levels']):
  offset=max(0,i-2)*1.25 if b['id']=='24457411' else 0
  shape=shapely.orient_polygons(poly.buffer(-offset,join_style=2))
  pieces=list(shape.geoms) if hasattr(shape,'geoms') else [shape]
  b['tiers'].append([dict(ring=list(g.exterior.coords)[:-1],triangles=[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(g).geoms]) for g in pieces])
actual_area=sum(Polygon(np.array(t)[:,:2]).area for t in triangles)
(D/'design.json').write_text(json.dumps(dict(roads=triangles,added_road_area=actual_area,requested_patch_area=missing.area,road_patches=len(parts),buildings=buildings,limits=['OSM road widths used where tagged; otherwise 2.6m paths and 7m road estimates.','Museum/bridge/steps/tunnel zones excluded from road patching.','Facade bays and setbacks interpreted from downloaded ACT front/top views, not surveyed dimensions.','Roof elevation derived from ACT points; OSM height retained.'])))
print('R161_DESIGN',missing.area,len(triangles),[(b['name'],b['roof'],b['base']) for b in buildings],flush=True)
