"""Fit a rigid XY placement to eight independently mapped OSM outline corners.

No scale change. This is a review candidate, not a surveyed correction.
"""
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.local_source_cache/gis_runtime'))
import numpy as np
c=json.loads((root/'config/foundation.json').read_text())['calibration']
p=json.loads((root/'config/pavilion_room.json').read_text())['footprint']
M=c['pdf_to_utm_matrix'];k=c['canonical_to_pdf_scale'];ox,oy=c['canonical_to_pdf_offset']
old=np.array([(M[0][0]*(k*x+ox)+M[0][1]*(k*y+oy)+M[0][2]-293425,M[1][0]*(k*x+ox)+M[1][1]*(k*y+oy)+M[1][2]-5499960) for x,y in p])
outline=json.loads((root/'.local_source_cache/act_context/mudam_exclusion.json').read_text())['polygon']
target=np.array([outline[i] for i in [7,8,9,10,3,4,5,6]])
delta=(target-old).mean(axis=0)
before=np.linalg.norm(target-old,axis=1);after=np.linalg.norm(target-old-delta,axis=1)
r=dict(accepted=False,source='OSM way 9042342, eight pavilion outline corner correspondences',old=old.tolist(),target=target.tolist(),translation_xy=delta.tolist(),before_corner_errors=before.tolist(),after_corner_errors=after.tolist(),rms_before=float(np.sqrt((before**2).mean())),rms_after=float(np.sqrt((after**2).mean())),limits=['Rigid translation only; no scale or architectural dimension changed.','OSM/ACT disagreement and incomplete facade-plane support remain; visual candidate only.','Link endpoint and source cut must follow placement before acceptance.'])
(root/'reports/R151_pavilion_registration_candidate.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
