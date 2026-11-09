from pathlib import Path
import sys,json,numpy as np
R=Path('12_Blender_Model');D=R/'.local_source_cache/r169';a=np.load(D/'164179154.npz');p=np.array(json.loads((D/'roof_planes_33.json').read_text())['points']);xmin,ymin=p[:,:2].min(0);xmax,ymax=p[:,:2].max(0);rng=np.random.default_rng(170);result=[]
for name,axis,edge,sgn in [('left',0,xmin,1),('right',0,xmax,-1),('rear',1,ymin,1),('front',1,ymax,-1)]:
 d=(p[:,axis]-edge)*sgn;other=p[:,1-axis];lo,hi=(ymin,ymax) if axis==0 else (xmin,xmax);mask=(d<2.5)&(other>lo+2)&(other<hi-2)&(p[:,2]<-62.7);q=p[mask];dd=d[mask];best=None;bc=0
 for _ in range(400):
  if len(q)<20:break
  ids=rng.choice(len(q),2,replace=False)
  if abs(dd[ids[0]]-dd[ids[1]])<.3:continue
  slope=(q[ids[0],2]-q[ids[1],2])/(dd[ids[0]]-dd[ids[1]])
  if not .5<slope<4:continue
  intercept=q[ids[0],2]-slope*dd[ids[0]];hit=abs(q[:,2]-slope*dd-intercept)<.2
  if hit.sum()>bc:bc=int(hit.sum());best=hit
 if best is None:result.append(dict(name=name,usable=False,samples=len(q)));continue
 c=np.linalg.lstsq(np.c_[dd[best],np.ones(bc)],q[best,2],rcond=None)[0];result.append(dict(name=name,axis=axis,edge=float(edge),sign=sgn,slope=float(c[0]),intercept=float(c[1]),support=bc,samples=len(q),rmse=float(np.sqrt(np.mean((dd[best]*c[0]+c[1]-q[best,2])**2))),usable=bc>=25))
(D/'mansard_planes_33.json').write_text(json.dumps(result,indent=2));print(result)
