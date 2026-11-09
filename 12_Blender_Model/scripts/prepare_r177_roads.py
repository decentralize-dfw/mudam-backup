from pathlib import Path
import json,sys,numpy as np
sys.path.insert(0,'12_Blender_Model/.local_source_cache/gis_runtime')
import shapely
from shapely.geometry import LineString,box
R=Path('12_Blender_Model');domain=box(-120,370,30,550);surfaces=[];marks=[]
for row in json.loads((R/'config/r177_merged_road_sources.json').read_text()):
 tag=row['tags'];h=tag.get('highway')
 if h not in ['secondary','tertiary','residential','service','path','footway','cycleway','pedestrian'] or tag.get('bridge') in ['yes','viaduct']:continue
 line=LineString(np.array(row['xy'])-[293425,5499960])
 if not line.intersects(domain):continue
 try:lanes=int(tag.get('lanes','1'))
 except:lanes=1
 width=float(tag['width']) if tag.get('width','').replace('.','').isdigit() else lanes*3.25 if h in ['secondary','tertiary','residential'] else 4 if h=='service' else 2.6
 poly=line.buffer(width/2,cap_style='flat',join_style='round').intersection(domain);tris=[]
 for x in np.arange(-120,30,3):
  for y in np.arange(370,550,3):
   g=poly.intersection(box(x,y,x+3,y+3))
   if not g.is_empty:tris.extend([list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(g).geoms if t.area>1e-7])
 if tris:surfaces.append(dict(id=row['id'],kind=h,tags=tag,width=width,triangles=tris))
 if h in ['secondary','tertiary'] and lanes>1:
  for j in range(1,lanes):
   lane=shapely.offset_curve(line,-width/2+j*width/lanes)
   if lane.geom_type!='LineString':continue
   for distance in np.arange(0,lane.length,9):
    g=LineString([lane.interpolate(distance),lane.interpolate(min(distance+3,lane.length))]).buffer(.06,cap_style='flat').intersection(domain)
    if not g.is_empty:marks.extend([list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(g).geoms if t.area>1e-7])
(R/'config/r177_road_reconstruction.json').write_text(json.dumps(dict(domain=[-120,370,30,550],surfaces=surfaces,markings=marks,limits=['OSM lane counts retained','Untagged lane widths3.25m provisional','Marked northern overhang region only']),indent=2));print([(r['id'],r['kind'],len(r['triangles'])) for r in surfaces],len(marks))
