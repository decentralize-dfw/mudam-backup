import json,sys
from pathlib import Path
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
D=json.loads((R/'reports/R495_EAST_RETURN_CREST_GROUND.json').read_text());q=np.array(D['controls']);print(D['coefficients'])
for lo in range(71,87,2):
 a=q[(q[:,0]>=lo)&(q[:,0]<lo+2)];print(lo,len(a),np.quantile(a[:,2],[0,.5,1]).round(3).tolist() if len(a) else [])
