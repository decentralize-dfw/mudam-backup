from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon
D=json.loads((R/'config/r301_ground_domains.json').read_text())
cover=shapely.union_all([Polygon([p[:2] for p in t['points']]) for t in D['triangles'] if Polygon([p[:2] for p in t['points']]).area>1e-9])
for d in D['domains']:
 p=Polygon([v[:2] for v in d['ring']]).buffer(0);gap=p.buffer(.5).difference(cover)
 print(d['name'],p.area,gap.area,gap.bounds)
