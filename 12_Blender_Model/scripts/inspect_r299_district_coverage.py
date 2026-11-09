import bpy,json,re,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R297_DOGU_GUNEY_CATI_MALZEME_ADAY_v001.blend'))
present={}
for o in bpy.context.scene.objects:
 m=re.fullmatch(r'R(?:171|174|182_DISTRICT)_(\d+)',o.name)
 if m:present[m[1]]=o.name
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text(encoding='utf8'));eligible=[];missing=[]
for w in ways:
 if 'building' not in w['tags'] or w['tags'].get('location')=='underground':continue
 p=np.array(w['xy'])-[293425,5499960];c=p.mean(0)
 if not(-600<c[0]<600 and -590<c[1]<-230):continue
 row=dict(id=w['id'],tags=w['tags'],polygon=p.tolist(),center=c.tolist(),object=present.get(str(w['id'])))
 eligible.append(row)
 if not row['object']:missing.append(row)
d=dict(eligible=len(eligible),modeled=len(present),missing=missing,scope='Existing lower-district rectangle -600..600 x -590..-230; not cadastral or whole user-region acceptance',present=present)
(R/'reports/R299_DISTRICT_COVERAGE.json').write_text(json.dumps(d,indent=2));print(d,flush=True)
