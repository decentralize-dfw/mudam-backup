import json,sys
from pathlib import Path
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from shapely.geometry import Polygon
w=json.loads(Path('10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text());rings=[np.array(next(q for q in w if str(q['id'])==i)['xy'])[:-1]-[293425,5499960] for i in ['37847302','123155868','123155867']];p=Polygon(rings[0],rings[1:]);pts=np.load(R/'.local_source_cache/r156/schuman_reference_points.npz')['xyz'];pts=pts[shapely.contains_xy(p.buffer(-1),pts[:,0],pts[:,1])];z=pts[:,2];hist,edge=np.histogram(z,bins=np.arange(15,55,.2));peak=edge[np.argmax(hist)];roof=float(np.median(z[(z>peak-.2)&(z<peak+.4)]));print('roof',roof,'quantiles',np.quantile(z,[.1,.5,.8,.95]))
pol=shapely.orient_polygons(p);rings=[list(pol.exterior.coords)[:-1]]+[list(q.coords)[:-1] for q in pol.interiors]
tris=[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(pol).geoms]
(R/'.local_source_cache/r156/schuman_clean.json').write_text(json.dumps(dict(rings=rings,roof_triangles=tris,roof=roof,base=roof-31,levels=9,source='OSM multipolygon1686713, outer37847302, courtyards123155868/123155867; ACT2020 roof altitude and facade reference')))
