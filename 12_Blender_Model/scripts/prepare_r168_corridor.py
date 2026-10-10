from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely,rasterio.features
from shapely.geometry import Polygon,box,shape
from affine import Affine
from scipy.ndimage import binary_erosion
from PIL import Image
traces=[[(30,540),(120,505),(290,481),(530,435),(615,410),(897,354),(1117,308),(1468,248),(1468,379),(1340,402),(1180,450),(955,493),(825,518),(620,556),(573,590),(260,580),(30,619)],[(530,435),(561,305),(617,151),(657,0),(724,0),(674,153),(630,294),(599,430)],[(865,355),(891,277),(1000,185),(1180,25),(1210,27),(1080,159),(955,282),(938,350)]]
polys=[Polygon([[-500+(300+2*x)*1150/4096,675-(650+2*y)*1150/4096] for x,y in trace]) for trace in traces];poly=shapely.union_all(polys);im=Image.open(R/'textures/R163_ACT_registered_surface.png').crop((300,650,3300,1950));alpha=np.asarray(im)[:,:,3];valid=binary_erosion(alpha>254,iterations=2);cov=shapely.union_all([shape(g) for g,v in rasterio.features.shapes(valid.astype('uint8'),mask=valid,transform=Affine(1150/4096,0,-500+300*1150/4096,0,-1150/4096,675-650*1150/4096)) if v]);poly=poly.intersection(cov);verts=[];faces=[]
for x in np.arange(poly.bounds[0],poly.bounds[2],2):
 for y in np.arange(poly.bounds[1],poly.bounds[3],2):
  p=box(x,y,x+2,y+2).intersection(poly)
  if p.is_empty or p.area<1e-7:continue
  for g in getattr(p,'geoms',[p]):
   if g.geom_type!='Polygon':continue
   for t in shapely.constrained_delaunay_triangles(g).geoms:
    if t.area<1e-7:continue
    t=shapely.orient_polygons(t);off=len(verts);verts.extend([[xx,yy,0] for xx,yy in list(t.exterior.coords)[:3]]);faces.append([off,off+1,off+2])
im.convert('RGB').save(R/'textures/R168_junction_source.png');D=R/'.local_source_cache/r168';D.mkdir(exist_ok=True);(D/'mesh.json').write_text(json.dumps(dict(vertices=verts,faces=faces)))
(R/'config/r168_junction.json').write_text(json.dumps(dict(area_m2=poly.area,source_crop=[300,650,3300,1950],traces_in_half_resolution_crop=traces,alpha_erosion_pixels=2,connected_components=len(getattr(poly,'geoms',[poly])),mesh_cache='.local_source_cache/r168/mesh.json',source='Manual road corridor outlines in registered ACT ortho; full source-covered main boulevard and two northern approaches.',limits=['Manual corridor outlines approximate, not surveyed kerbs.','Crossings, lanes, tram median and sidewalks are registered source color on authored terrain-conforming mesh.','Road elevation follows existing terrain; cars, shadows and vegetation occlusion remain baked in source.','Corridor ends at available source coverage; wider road network remains incomplete.']),indent=2));print('R168',poly.area,len(faces))
