import json,sys
from pathlib import Path
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
D=json.loads((R/'reports/R487_PASSAGE_PLANE.json').read_text());q=np.array(D['controls']);e=np.c_[np.ones(len(q)),q[:,0]+45,q[:,1]-24]@D['coefficients']-q[:,2];print(np.c_[q,e][np.argsort(abs(e))[-12:]].round(3))
