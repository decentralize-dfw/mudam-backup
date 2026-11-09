from pathlib import Path
import sys,json,numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import LineString,Polygon
rows=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text());lookup={r['id']:r for r in rows}
def xy(id):return [(x-293425,y-5499960) for x,y in lookup[id]['xy']]
path=xy('172705752')+xy('26435587')[1:]+xy('840229557')[1:]
center=LineString(path).offset_curve(1.82,join_style=2);footprint=Polygon(xy('1512745574'));bridge=center.intersection(footprint)
if bridge.geom_type!='LineString':raise RuntimeError(bridge.geom_type)
p=[list(bridge.interpolate(float(s)).coords[0]) for s in np.linspace(0,bridge.length,int(np.ceil(bridge.length))+1)]
out=dict(source_ways=['172705752','26435587','840229557','1512745574'],source='Existing OSM UTM; full bridge outline and railway alignment',bridge_length=bridge.length,centerline=p,footprint=xy('1512745574'),limits=['Centerline shifted1.82m from mapped first track; cross-check second track','South beyond ACT coverage cannot have scan-verified arches'])
(R/'config/r200_bridge_alignment.json').write_text(json.dumps(out,indent=2));print('LENGTH',bridge.length,'ENDS',p[0],p[-1])
