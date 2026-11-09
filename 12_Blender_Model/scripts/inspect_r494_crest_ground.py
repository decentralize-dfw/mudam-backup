import json,sys
from pathlib import Path
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
D=json.loads((R/'reports/R494_WALL_CREST_GROUND.json').read_text());q=np.array(D['controls']);print(D['coefficients'])
for lo in range(49,73,3):
 a=q[(q[:,0]>=lo)&(q[:,0]<lo+3)];print(lo,np.round(a,2).tolist())
