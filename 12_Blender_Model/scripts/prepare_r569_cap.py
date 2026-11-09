from pathlib import Path
import sys,json
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'));import numpy as np
r=json.loads((R/'reports/R563_RETURN_PLATEAU_CELLS.json').read_text());s=json.loads((R/'reports/R568_CAP_WIDTH_SECTIONS.json').read_text());rows=[]
for q in r:
 if 49.5<q['x']<50.5 and q['y']>=-57.5 and -2.05<q['z'][1]<-1.6:rows.append([q['x'],q['y'],q['z'][1],'return_unclassified'])
for q in s:
 if q['classification']==2 and q['z'][1]>-1.85 and q['z'][2]-q['z'][0]<.3 and ((q['x']<=54 and 0<=q['offset']<=.5)or(q['x']>=56 and .25<=q['offset']<=1.5)):rows.append([q['x'],q['y'],q['z'][1],'cap_classified'])
p=np.array([v[:3]for v in rows]);A=np.array([[1,x-49.5,y+58,max(x-54,0),max(x-56,0)]for x,y,z in p]);train=np.arange(len(p))%4!=0;c=np.linalg.lstsq(A[train],p[train,2],rcond=None)[0];e=A[~train]@c-p[~train,2];D=dict(coefficients=c.tolist(),training=int(sum(train)),heldout=int(sum(~train)),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),controls=rows,source='R568 classified cap plateau and sharp drop to interior paving. Return unclassified plateau remains provisional. Previous2m cap covers measured floor at western end: rejected width.')
(R/'reports/R569_CONTINUOUS_CAP_PLANES.json').write_text(json.dumps(D,indent=2));print(c,D['rms'],D['max'])
