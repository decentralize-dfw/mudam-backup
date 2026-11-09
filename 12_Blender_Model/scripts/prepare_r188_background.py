from pathlib import Path
import sys,json,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,LineString
from shapely.ops import polygonize,unary_union,triangulate
from pyproj import Transformer
root=ET.parse(R/'references/R176_north_osm.xml').getroot();tr=Transformer.from_crs(4326,32632,always_xy=True)
nodes={}
for e in root.findall('node'):
 x,y=tr.transform(float(e.attrib['lon']),float(e.attrib['lat']));nodes[e.attrib['id']]=(x-293425,y-5499960)
ways={e.attrib['id']:[nodes[n.attrib['ref']] for n in e.findall('nd') if n.attrib['ref'] in nodes] for e in root.findall('way')}
data=json.loads((R/'config/r176_north_footprints.json').read_text());out=[]
for rid in ['51071558','rel18163400']:
 row=next(r for r in data if r['id']==rid);poly=Polygon(row['ring'])
 if rid.startswith('rel'):
  rel=next(e for e in root.findall('relation') if e.attrib['id']==rid[3:]);holes=[]
  lines=[LineString(ways[e.attrib['ref']]) for e in rel.findall('member') if e.attrib.get('role')=='inner' and e.attrib.get('ref') in ways]
  if lines:holes=list(polygonize(unary_union(lines)))
  for h in holes:poly=poly.difference(h)
 if not poly.is_valid:raise RuntimeError('Invalid footprint '+rid)
 out.append(dict(id=rid,name=row['tags']['name'],height=float(row['tags']['height']),outer=list(poly.exterior.coords)[:-1],holes=[list(h.coords)[:-1] for h in poly.interiors],triangles=[list(t.exterior.coords)[:-1] for t in triangulate(poly) if poly.covers(t)],area=poly.area))
(R/'config/r188_background_domains.json').write_text(json.dumps(out,indent=2))
print([(r['id'],r['area'],len(r['holes'])) for r in out])
