import json
from pathlib import Path
p=Path('10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json');d=json.loads(p.read_text(encoding='utf-8-sig'));print(type(d).__name__)
if isinstance(d,dict):print(list(d)[:6])
else:
 for v in d:
  if str(v.get('id'))=='563325237':print(v)
