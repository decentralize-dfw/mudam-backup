from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_whole_roof_samples_v061.json').read_text());p=np.array(d['vertices']);xy=p[:,:2];center=xy.mean(0);A=np.c_[xy-center,np.ones(len(p))];z=p[:,2];rng=np.random.default_rng(16965);remaining=np.ones(len(p),bool);models=[];labels=np.full(len(p),-1)
for k in range(12):
 ids=np.where(remaining)[0]
 if len(ids)<120:break
 best=None;score=0
 for _ in range(350):
  sample=rng.choice(ids,3,replace=False)
  try:c=np.linalg.solve(A[sample],z[sample])
  except np.linalg.LinAlgError:continue
  if np.linalg.norm(c[:2])>3:continue
  err=abs(A[ids]@c-z[ids]);mask=err<.09;count=int(mask.sum())
  if count>score:best=c;score=count
 if score<120:break
 for _ in range(4):
  inliers=ids[abs(A[ids]@best-z[ids])<.09];best=np.linalg.lstsq(A[inliers],z[inliers],rcond=None)[0]
 labels[inliers]=k;remaining[inliers]=False;models.append(dict(coeff=best.tolist(),count=len(inliers)));print(k,len(inliers),best)
# Only coherent neighbours share a fitted plane; isolated retained features remain measured.
nx=d['nx'];ny=d['ny'];lab=labels.reshape(ny,nx);out=p.copy();moved=0
for j in range(1,ny-1):
 for i in range(1,nx-1):
  k=j*nx+i;label=lab[j,i]
  if label<0 or np.count_nonzero(lab[j-1:j+2,i-1:i+2]==label)<6:continue
  out[k,2]=A[k]@np.array(models[label]['coeff']);moved+=1
d['vertices']=out.tolist();d['plane_cleaning']=dict(models=models,coherent_projected_vertices=moved,max_height_change=float(abs(out[:,2]-z).max()),limits='Main measured plane inliers only; discontinuous roof features and edge vertices retained.')
(D/'row_whole_roof_samples_v065.json').write_text(json.dumps(d));print('PROJECTED',moved,d['plane_cleaning']['max_height_change'])
