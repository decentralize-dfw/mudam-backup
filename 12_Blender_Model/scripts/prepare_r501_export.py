from pathlib import Path
R=Path(__file__).resolve().parents[1]
scene='MUDAM_R501_BATI_SUR_AGAC_KOTU_DUZELTME_ADAY_v001.blend'
p=R/'scripts/export_r492_review.py';s=p.read_text().replace('MUDAM_R492_SUR_CEVRE_UV_DUZELTME_ADAY_v001.blend',scene).replace('<=492','<=501').replace('R492','R501').replace('r492','r501');(R/'scripts/export_r501_review.py').write_text(s)
p=R.parent/'web/scripts/prepare-r492-review.mjs';s=p.read_text().replace('MUDAM_R492_SUR_CEVRE_UV_DUZELTME_ADAY_v001.blend',scene).replace('R492','R501').replace('r492','r501');(p.parent/'prepare-r501-review.mjs').write_text(s)
