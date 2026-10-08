"""NumPy perspective camera fitting, no geometry optimization or image warping."""
import numpy as np

def basis(p):
 yaw,pitch,roll=p[3:6];sy,cy=np.sin(yaw),np.cos(yaw)
 f=np.array([sy*np.cos(pitch),cy*np.cos(pitch),np.sin(pitch)])
 r=np.array([cy,-sy,0]);u=np.cross(r,f)
 return np.array([r*np.cos(roll)+u*np.sin(roll),u*np.cos(roll)-r*np.sin(roll),f])

def project(p,points,size):
 q=(np.array(points)-p[:3])@basis(p).T
 return np.array(size)/2+np.exp(p[6])*q[:,:2]/q[:,2,None]*[1,-1]

def solve(points,pixels,size,starts,bounds,max_iter=220):
 points=np.array(points);pixels=np.array(pixels);lo,hi=map(np.array,bounds)
 def residual(p):return (project(p,points,size)-pixels).ravel()
 best=None;runs=[]
 for start in starts:
  p=np.array(start,float);damping=1e-2
  for iteration in range(max_iter):
   r=residual(p);eps=np.array([1e-3]*3+[1e-6]*4)
   jac=np.column_stack([(residual(p+np.eye(7)[i]*eps[i])-r)/eps[i] for i in range(7)])
   a=jac.T@jac
   try:delta=np.linalg.solve(a+damping*np.diag(np.maximum(np.diag(a),1e-8)),-jac.T@r)
   except np.linalg.LinAlgError:break
   q=p+delta
   valid=np.all(q>lo)&np.all(q<hi)
   if valid and np.linalg.norm(residual(q))<np.linalg.norm(r):
    p=q;damping=max(damping/3,1e-10)
    if np.linalg.norm(delta)<1e-8:break
   else:
    damping=min(damping*5,1e12)
    if damping>=1e12:break
  cost=float(np.sqrt(np.mean(np.sum(residual(p).reshape(-1,2)**2,axis=1))))
  runs.append(dict(rmse_px=cost,camera=p.tolist()))
  if best is None or cost<best[0]:best=(cost,p)
 return best[1],runs
