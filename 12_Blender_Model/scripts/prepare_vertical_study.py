"""Conditional section-based height study, never a surveyed/as-built solution."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
C=json.loads((B/'config/foundation.json').read_text(encoding='utf8'))['calibration']
m=C['meters_per_canonical_pixel']
# Homologous *candidate* horizontal spans, not a recovered section cut line.
spans=[dict(name='Pavilion outer width',section=[1074,1238],plan=[42,171]),
       dict(name='Main roof outer width',section=[410,695],plan=[462,688]),
       dict(name='Pavilion link',section=[919,1074],plan=[171,289])]
for p in spans:p['m_per_section_px']=abs(p['plan'][1]-p['plan'][0])*m/abs(p['section'][1]-p['section'][0])
scale=float(np.median([p['m_per_section_px'] for p in spans]));lo=min(p['m_per_section_px'] for p in spans);hi=max(p['m_per_section_px'] for p in spans)
# Y picks at visible drawing lines. 2 px sensitivity on both baseline and target.
datum=436
picks={'Z_LP1_FINISH':384,'Z_LM1_FINISH':493,'Z_TECH_FINISH':550,
 'Z_ROOF_MAIN_BASE':287,'Z_ROOF_MAIN_APEX':111,'Z_PAV_FINISH':436,
 'Z_PAV_LM1_FINISH':477,'Z_PAV_WALL_TOP':378,'Z_PAV_SHOULDER':339,'Z_PAV_LANTERN_TOP':299,'Z_PAV_APEX':280,
 'Z_LINK_CEILING':391}
params=[]
for ident,y in picks.items():
 vals=[(datum+dy0-y-dy1)*s for dy0 in [-2,2] for dy1 in [-2,2] for s in [lo,hi]]
 params.append(dict(id=ident,draft_value=(datum-y)*scale,min=min(vals),max=max(vals),section_y_px=y,status='conditional_section_estimate',source_ids=['101','102'],value=None))
data=dict(version=1,source='101',ground_y_px=datum,section_m_per_px=scale,span_checks=spans,
 conditional_assumptions=['Section image uses the same vertical and horizontal scale.',
 'Candidate horizontal correspondences refer to comparable projected widths.',
 'Spiral-stair doorway bottom near y=384 is an upper finish candidate; main-stair landing is obscured and stair-count verification pending.',
 '2016 vector and current visitor diagrams represent compatible permanent geometry.'],
 uncertainty_note='Intervals only express span disagreement and +/-2px picking sensitivity. They are NOT statistical confidence intervals and exclude OSM/source/date/projection errors.',
 section_cut_line_in_plan=None,section_original_date=None,as_built_verified=False,
 parameters=params,external_crosscheck=dict(url='https://lcb.lu/en/partners/122?favorite=show',accessed='2026-10-08',published_ceiling_heights_m={'Grand Hall':33,'Foyer':4.67,'Passerelle':6},use='Context only; room ceiling heights are not floor elevations. 33m does not establish roof-apex datum.'),
 excluded_elements=['Central coloured pavilion in section: permanent/temporary identity unresolved.', 'Construction thicknesses, step counts, rails, glazing and steel sections are unmeasured.'])
(B/'config/vertical_study.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
P=R/'11_Blender_Modelleme_Plani/parametreler.json';doc=json.loads(P.read_text(encoding='utf8'))
byid={p['id']:p for p in params}
for p in doc['parameters']:
 if p['id'] in byid:
  q=byid[p['id']];p.update({k:q[k] for k in ['draft_value','min','max','status']});p['method']='101 section proportional study; vertical_study.json';p['notes']=data['uncertainty_note'];p['value']=None
 if p['id'] in ['Z_PAV_FINISH','LINK_FLOOR_SLOPE']:
  p['source_ids']=[s for s in p['source_ids'] if s!='066'];p['notes']+=' 066 is a separate stepped glass stair; not the flat pavilion link.'
P.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf8')
# Annotated source remains a separate derived image. Original unchanged.
im=Image.open(R/'02_Kesitler/101_Mimari_kesit_ArchEyes.jpg').convert('RGB');d=ImageDraw.Draw(im)
for p in params:
 if p['id'].startswith('Z_PAV') or p['id']=='Z_LINK_CEILING':continue
 y=p['section_y_px'];d.line([(90,y),(950,y)],fill='#c44b24',width=1)
 d.text((20,y-13),f"{p['id']}  {p['draft_value']:+.2f} m (DRAFT)",fill='#aa3010')
d.text((20,650),'CONDITIONAL HEIGHT STUDY / NOT AS-BUILT / section cut line and date unresolved',fill='black')
d.text((20,673),f'Section scale: {scale:.5f} m/px; ground datum y=436; span/pick sensitivity only.',fill='black')
im.save(B/'references/P04_section_height_study.png')
print(json.dumps({'section_scale':scale,'parameters':{p['id']:round(p['draft_value'],3) for p in params}},indent=2))
