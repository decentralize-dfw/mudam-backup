from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon
from shapely import constrained_delaunay_triangles
parts=json.loads((R/'config/r176_authored_parts.json').read_text());edges={r['name']:r for r in json.loads((R/'reports/R206_ROOF_EDGE_MEASUREMENTS.json').read_text())};planes=json.loads((R/'config/r206_novotel_roof_planes.json').read_text());out=[]
for p in planes:
 row=next(r for r in parts if r['name']==p['name']);outer=Polygon(row['outer'],row['holes']);inner=outer.buffer(-.24,join_style=2);band=outer.difference(inner);p.update(dict(outer=list(outer.exterior.coords)[:-1],inner=list(inner.exterior.coords)[:-1],curb_triangles=[list(t.exterior.coords)[:-1] for t in constrained_delaunay_triangles(band).geoms],parapet=edges[p['name']]['parapet_top'],source_edges=edges[p['name']],old_top=row['top']));out.append(p)
(R/'config/r206_closed_roofs.json').write_text(json.dumps(out,indent=2))
