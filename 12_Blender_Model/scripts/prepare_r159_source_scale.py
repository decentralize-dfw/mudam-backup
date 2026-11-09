from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from scipy.spatial import cKDTree
D=R/'.local_source_cache/r158';d=json.loads((D/'trees.json').read_text());a=np.load(D/'act_canopy.npz');rows,cols=np.where(a['mask']);xy=np.column_stack((-500+(cols+.5)*2,-450+(rows+.5)*2));stems=np.array([t['xy'] for t in d['trees']]);_,labels=cKDTree(stems).query(xy)
for i,t in enumerate(d['trees']):
 cells=xy[labels==i];assert len(cells)
 low=cells.min(0)-1;high=cells.max(0)+1
 # These bounds describe the assigned source-canopy patch, not a surveyed trunk/crown.
 t['canopy_patch_bounds_xy']=[low.tolist(),high.tolist()]
 selected=labels==i
 t['source_top_z']=float(a['top'][rows[selected],cols[selected]].max());t['source']='ACT source canopy patch: raw surface top and assigned 2m cells; individual stem inferred'
out=R/'.local_source_cache/r159';out.mkdir(exist_ok=True);(out/'scaled_trees.json').write_text(json.dumps(d));print('R159_SOURCE_SCALE',len(d['trees']),flush=True)
