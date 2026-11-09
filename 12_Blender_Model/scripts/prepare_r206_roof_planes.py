from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];rows=json.loads((R/'reports/R203_INTERIOR_ROOF_LEVELS.json').read_text());out=[];rng=np.random.default_rng(203)
for r in rows:
 a=np.array(r['samples']);org=a[:,:2].mean(0);X=np.c_[a[:,:2]-org,np.ones(len(a))];best=None
 for _ in range(800):
  ids=rng.choice(len(a),3,False)
  if abs(np.linalg.det(X[ids]))<.2:continue
  c=np.linalg.solve(X[ids],a[ids,2])
  if np.linalg.norm(c[:2])>.08:continue
  mask=abs(X@c-a[:,2])<.15
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(X[best],a[best,2],rcond=None)[0];err=abs(X@c-a[:,2]);out.append(dict(name=r['name'],origin=org.tolist(),plane=c.tolist(),inliers=int(best.sum()),samples=len(a),support=float(best.mean()),inlier_p90=float(np.quantile(err[best],.9))))
(R/'config/r206_novotel_roof_planes.json').write_text(json.dumps(out,indent=2));print(out)
