from pathlib import Path
import sys,json
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
ret=json.loads((R/'reports/R563_RETURN_PLATEAU_CELLS.json').read_text());south=json.loads((R/'reports/R564_SOUTH_CAP_CELLS.json').read_text());a,b,c=json.loads((R/'reports/R529_SOUTH_FACE_PLANE.json').read_text())['plane'];rows=[]
for r in ret:
 if 49.5<r['x']<50.5 and r['y']>=-58 and -2.05<r['z'][1]<-1.6:rows.append([r['x'],r['y'],r['z'][1]])
for r in south:
 if 50.5<=r['x']<=64:rows.append([r['x'],a*r['x']+b*r['z'][1]+c+.95,r['z'][1]])
p=np.array(rows);A=np.array([[1,x-49.5,y+58,max(x-54.5,0),max(x-56,0)]for x,y,z in rows]);train=np.arange(len(p))%4!=0;coef=np.linalg.lstsq(A[train],p[train,2],rcond=None)[0];res=A[~train]@coef-p[~train,2];D=dict(coefficients=coef.tolist(),training=int(sum(train)),heldout=int(sum(~train)),rms=float(np.sqrt(np.mean(res**2))),max=float(abs(res).max()),controls=rows,source='Class1 return plateau plus southern cap strip medians, bounded by OSM wall trace and class2 grade discontinuity. Vegetation cannot be excluded everywhere; candidate only.')
(R/'reports/R565_CONTINUOUS_CAP_PLANES.json').write_text(json.dumps(D,indent=2));print(D['coefficients'],D['rms'],D['max'])
