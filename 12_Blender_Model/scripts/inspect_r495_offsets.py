import json,sys
from pathlib import Path
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
D=json.loads((R/'reports/R495_EAST_RETURN_CREST_GROUND.json').read_text());q=np.array(D['controls']);a=np.array([72.1308731,-56.2978676]);t=np.array([14.3192405,16.5089074]);t/=np.linalg.norm(t);n=np.array([-t[1],t[0]]);s=(q[:,:2]-a)@t;u=(q[:,:2]-a)@n;print(np.c_[s,u,q[:,2]][np.argsort(q[:,0])].round(3).tolist())
