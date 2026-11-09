import json
from pathlib import Path
R=Path('12_Blender_Model')
for v in json.loads((R/'reports/R349_PAVILION_WALLS.json').read_text()):print(v['name'],v['min'],v['max'])
