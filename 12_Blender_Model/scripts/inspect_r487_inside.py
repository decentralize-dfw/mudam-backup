import json,sys
from pathlib import Path
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
q=np.array(json.loads((R/'reports/R487_LOWER_PASSAGE_GRADE.json').read_text())['controls']);q=q[(q[:,0]-q[:,1]>-68.7)]
for lo,hi in [(12,18),(18,24),(24,30),(30,36),(36,42)]:
 a=q[(q[:,1]>=lo)&(q[:,1]<hi)];print(lo,hi,len(a),np.round(np.quantile(a[:,2],[0,.25,.5,.75,1]),3) if len(a) else '')
print(q.shape)
