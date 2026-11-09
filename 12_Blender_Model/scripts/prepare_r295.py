from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
ds=json.loads((R/'config/r291_south_roof.json').read_text());d=ds[0]
d['boundarySource']='R291_south_roof_source.png'
d['boundaryPixels']=[(100,1023),(1018,454),(799,218),(665,150)]
d['polygon']=[[175+x*.125,152-y*.125] for x,y in d['boundaryPixels']]
a,b,c=d['plane'];ox,oy=d['origin'];d['cornerRoofs']=[a*(x-ox)+b*(y-oy)+c for x,y in d['polygon']]
(R/'config/r295_south_roof.json').write_text(json.dumps(ds,indent=2))
s=(R/'scripts/build_r292_south_roof.py').read_text().replace('R292','R295').replace('r292','r295').replace('r291_south_roof.json','r295_south_roof.json')
s=s.replace('lightRecords=[]',"lights.append((650,188,15,24,[.55,-.835]))\nlightRecords=[]")
s=s.replace('40 rectangular and 6 round','41 rectangular and 6 round')
(R/'scripts/build_r295_south_roof.py').write_text(s)
