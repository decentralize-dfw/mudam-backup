"""Prepare independent wall/ramp reconstruction from measured section controls.

No scan vertices/faces are transferred. Only three architectural corner controls
and two planar grade domains are used; source uncertainty remains explicit.
"""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
rows=json.loads((R/'reports/R321_WEST_CREST_MEASUREMENTS.json').read_text())
sections=json.loads((R/'reports/R323_CREST_SECTIONS.json').read_text())
for i,px,py in [(5,598,599),(6,640,599),(7,669,604)]:
    sample=next(p for s in sections for p in s if p['pixel']==[px,py])
    rows[i]['previousCrest']=rows[i]['measuredCrest']
    rows[i]['measuredCrest']=sample['xyz']
    rows[i]['measurement']='Outer ramp edge immediately before moat drop; section R323'
(R/'reports/R323_WEST_CREST_CONTROLS.json').write_text(json.dumps(rows,indent=2))
s=(R/'scripts/build_r321_west_retaining_wall.py').read_text()
s=s.replace('R321_WEST_CREST_MEASUREMENTS.json','R323_WEST_CREST_CONTROLS.json')
s=s.replace('MUDAM_R321_BATI_HENDEK_ISTINAT_ADAY_v001','MUDAM_R323_BATI_RAMPA_SUR_ADAY_v001')
s=s.replace('r321_west_retaining_REVIEW','r323_west_retaining_REVIEW')
s=s.replace('R321_west_retaining.png','R323_west_retaining.png').replace('R321_WEST_RETAINING.json','R323_WEST_RETAINING.json')
s=s.replace('candidate, crest station6 and width require further source verification','candidate; three outer ramp corners revised from source sections; width remains provisional')
s=s.replace('Station6 source fit uncertain','Three outer ramp stations revised; width and remaining corners still require comparison')
(R/'scripts/build_r323_west_ramp_wall.py').write_text(s)
s=(R/'scripts/build_r322_west_museum_terrace.py').read_text()
s=s.replace('MUDAM_R321_BATI_HENDEK_ISTINAT_ADAY_v001','MUDAM_R323_BATI_RAMPA_SUR_ADAY_v001')
s=s.replace('R321_WEST_CREST_MEASUREMENTS.json','R323_WEST_CREST_CONTROLS.json')
s=s.replace('MUDAM_R322_BATI_MUZE_TERAS_KOT_ADAY_v004','MUDAM_R323_BATI_RAMPA_TERAS_ADAY_v001')
s=s.replace('r322_west_terrain_REVIEW','r323_west_ramp_terrain_REVIEW')
s=s.replace('R322_west_terrace_v004.png','R323_west_ramp_terrace_v001.png').replace('R322_WEST_TERRACE.json','R323_WEST_RAMP_TERRACE.json')
# The three outer edge controls form a longitudinal ramp. The terrace remains
# at the source upper grade until the sharp grade break at pixel row 568.
# A short cross-grade bank meets the ramp at row 581. This is an analytic
# reconstruction of two domains, not a remeshed scan surface.
s=s.replace(' return best[1]*(1-w)+near[1]*w', ''' value=best[1]*(1-w)+near[1]*w
 px=(p.x+120)*1400/220;py=(95-p.y)*1400/220
 if 598<=px<=669 and py>=568:
  t=(px-598)/71
  ramp=-6.02+(-3.73+6.02)*t
  cross=max(0,min(1,(py-568)/13))
  value=-3.34*(1-cross)+ramp*cross
 return value''')
s=s.replace("points=list(poly)","""points=list(poly)
for py in [568,581]:
 for px in range(598,670,2):
  p=(-120+px*220/1400,95-py*220/1400)
  if inside(Vector(p)):points.append(p)
""")
s=s.replace('Retaining station6 crest needs independent refinement','Ramp and upper terrace are separate analytic grade domains; width and adjoining limits remain candidates')
(R/'scripts/build_r323_west_ramp_terrace.py').write_text(s)
print('R323_BUILDERS_READY')
