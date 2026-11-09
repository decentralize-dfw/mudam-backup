import json
from pathlib import Path
d=json.loads(Path('10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text(encoding='utf-8-sig'))
for w in d:
 if w['tags'].get('barrier') not in ['city_wall','retaining_wall','wall']:continue
 xy=[[a-293425,b-5499960] for a,b in w['xy']]
 if min(x for x,y in xy)<80 and max(x for x,y in xy)>45 and min(y for x,y in xy)<-50 and max(y for x,y in xy)>-68:print(w['id'],w['tags'],xy)
