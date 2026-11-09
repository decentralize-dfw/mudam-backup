import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union,split
from shapely import constrained_delaunay_triangles,set_precision
poly=set_precision(unary_union([Polygon(t)for t in json.loads((R/'reports/R548_SLOPE_FOOTPRINT.json').read_text())if Polygon(t).area>1e-8]),.0001);parts=[poly]
for x in (-20,-16):parts=[g for p in parts for g in split(p,LineString([(x,-10),(x,10)])).geoms]
d=json.loads((R/'reports/R548_SLOPE_PLANES.json').read_text());d['triangles']=[list(t.exterior.coords)[:3]for p in parts for t in constrained_delaunay_triangles(p).geoms];(R/'reports/R548_SLOPE_DESIGN.json').write_text(json.dumps(d,indent=2))
