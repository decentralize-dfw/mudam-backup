from pathlib import Path
import json,sys,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from scipy.optimize import least_squares
d=json.loads((R/'reports/R502_ROOF_RADIAL_PROFILES.json').read_text());out=[]
for tower in d['source']:
 rows=[];cx,cy=tower['center']
 for threshold in [4.55,4.65,4.75]:
  pts=[]
  for sector,s in enumerate(tower['sections']):
   pp=s['points'];cross=None
   for a,b in zip(pp,pp[1:]):
    if a[1] is not None and b[1] is not None and a[1]>=threshold>b[1] and a[0]>(2 if tower['tower']=='CENTRE' else 3.5):cross=a[0]+(b[0]-a[0])*(a[1]-threshold)/(a[1]-b[1]);break
   if cross is not None:pts.append([cx+cross*math.cos(s['angle']),cy+cross*math.sin(s['angle']),sector])
  p=np.array(pts);test=p[:,2].astype(int)%4==0
  def residual(x,q):return np.linalg.norm(q[:,:2]-x[:2],axis=1)-x[2]
  fit=least_squares(residual,[cx,cy,2.8 if tower['tower']=='CENTRE' else 4.5],args=(p[~test],),loss='soft_l1',f_scale=.08);e=residual(fit.x,p[test]);rows.append(dict(threshold=threshold,fit=fit.x.tolist(),points=p.tolist(),training=int((~test).sum()),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max())))
 out.append(dict(tower=tower['tower'],oldCenter=tower['center'],trials=rows))
(R/'reports/R503_TOWER_EDGE_CIRCLE_FITS.json').write_text(json.dumps(out,indent=2));print([{**{k:v for k,v in t.items() if k!='trials'},'trials':[{k:v for k,v in a.items() if k!='points'} for a in t['trials']]}for t in out])
