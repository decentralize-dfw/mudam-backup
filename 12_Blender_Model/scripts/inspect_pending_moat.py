import json
from pathlib import Path
R=Path('12_Blender_Model')
d=json.loads((R/'reports/R335_OUTER_MOAT_REMAINDER.json').read_text())
for k,v in d.items():print(k,{a:v.get(a) for a in ['outline','valid','rms','maxAbsolute','heldOut','training','plane']})
