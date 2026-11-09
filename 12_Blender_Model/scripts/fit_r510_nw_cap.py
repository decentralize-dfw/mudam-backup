from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
d=json.loads((R/'reports/R510_NW_CAP_SOURCE_GRID.json').read_text());q=np.array([[p['x'],p['y'],p['u'],p['z']] for p in d if -71<=p['u']<=-69 and 19<=p['y']<=39 and p['normal'][2]>.85 and p['z']<0]);x,y,u,z=q.T;keys=np.round((y-18)*2).astype(int);test=keys%4==0;M=np.c_[np.ones(len(q)),y-28,np.maximum(0,y-21.5),np.maximum(0,y-24),u+69.8];coef=np.linalg.lstsq(M[~test],z[~test],rcond=None)[0];err=M[test]@coef-z[test];out=dict(coefficients=coef.tolist(),training=int((~test).sum()),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(err**2))),max=float(abs(err).max()),controls=q.tolist(),method='Independent longitudinal three-plane grade plus constant crossfall on visible upward-facing interior cap controls; excluded vertical edge smear by normal, no surface copy.');(R/'reports/R510_NW_CAP_FIT.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='controls'})
for yy in [20,24,28,32,36,40]:print(yy,[(p['u'],round(p['z'],2),round(p['normal'][2],2)) for p in d if p['y']==yy])
