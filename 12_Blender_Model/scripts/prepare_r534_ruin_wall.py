import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
d=json.loads((R/'reports/R533_RUIN_WALL_CAP.json').read_text());fits={}
for seg in [0,5]:
 rows=[r for r in d['rows']if r['segment']==seg and (seg!=5 or r['t']<.94)];q=np.array([[r['t'],np.median([h['z']for h in r['hits']])]for r in rows]);A=np.c_[np.ones(len(q)),q[:,0]];test=np.arange(len(q))%4==0;c=np.linalg.lstsq(A[~test],q[~test,1],rcond=None)[0];e=A[test]@c-q[test,1];fits[str(seg)]=dict(coefficients=c.tolist(),heldout=dict(count=int(sum(test)),rms=float(np.sqrt(np.mean(e*e))),max=float(max(abs(e)))))
line=d['line'];stations=[]
for i,xy in enumerate(line):
 if i==0:z=fits['0']['coefficients'][0]
 elif i==1:z=sum(fits['0']['coefficients'])
 elif i==5:z=fits['5']['coefficients'][0]
 elif i==6:z=sum(fits['5']['coefficients'])
 else:z=sum(fits['0']['coefficients'])*(5-i)/4+fits['5']['coefficients'][0]*(i-1)/4
 stations.append([*xy,z])
(R/'reports/R534_RUIN_WALL_DESIGN.json').write_text(json.dumps(dict(stations=stations,fits=fits,capWidth=.65,source='R533_east_ruin_full_source.png; cap centreline traced, independent linear grades; width trace estimate',accepted=False),indent=2));print(fits)
