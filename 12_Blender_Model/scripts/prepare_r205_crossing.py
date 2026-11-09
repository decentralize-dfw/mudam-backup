from pathlib import Path
import sys,json,numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,LineString
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text());r=next(w for w in ways if w['id']=='1289754033');xy=(np.array(r['xy'])-[293425,5499960]).tolist();p=Polygon(xy);hits=[]
for w in ways:
 if not w['tags'].get('highway'):continue
 line=LineString(np.array(w['xy'])-[293425,5499960])
 if p.intersects(line):hits.append(dict(id=w['id'],tags=w['tags']))
(R/'config/r205_river_crossing.json').write_text(json.dumps(dict(footprint=xy[:-1],source=r['id'],tags=r['tags'],ways=hits),indent=2));print(hits)
