"""Planar polygon union by splitting source edges and retaining union boundary.
Uses float64 Python arithmetic, so coplanar 3-D booleans are unnecessary.
Input: simple closed polygons without repeated last vertex. Output: CCW boundary loops.
"""
import math

def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def add(a,b,t):return (a[0]+b[0]*t,a[1]+b[1]*t)
def inside(p,poly):
 result=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:result=not result
 return result

def union(polygons,tol=1e-7):
 polys=[[tuple(map(float,p[:2])) for p in poly] for poly in polygons];edges=[(a,b) for poly in polys for a,b in zip(poly,poly[1:]+poly[:1]) if math.dist(a,b)>tol];boundary={}
 for a,b in edges:
  v=sub(b,a);length=math.hypot(*v);ts=[0.,1.]
  for c,d in edges:
   w=sub(d,c);den=cross(v,w);ca=sub(c,a)
   if abs(den)>tol:
    t=cross(ca,w)/den;u=cross(ca,v)/den
    if -tol<=t<=1+tol and -tol<=u<=1+tol:ts.append(min(1.,max(0.,t)))
   elif abs(cross(ca,v))<tol*length:
    for p in [c,d]:
     t=sum(x*y for x,y in zip(sub(p,a),v))/(length*length)
     if tol<t<1-tol:ts.append(t)
  ts=sorted(ts)
  for t0,t1 in zip(ts,ts[1:]):
   if (t1-t0)*length<tol:continue
   p,q=add(a,v,t0),add(a,v,t1);m=add(a,v,(t0+t1)/2);eps=min(1e-5,(t1-t0)*length*.1);n=(-v[1]/length*eps,v[0]/length*eps)
   left=any(inside(add(m,n,1),poly) for poly in polys);right=any(inside(add(m,n,-1),poly) for poly in polys)
   if left==right:continue
   if right:p,q=q,p
   k,j=tuple(round(x,6) for x in p),tuple(round(x,6) for x in q)
   if k!=j:boundary[(k,j)]=(p,q)
 outgoing={}
 for (k,j),(p,q) in boundary.items():outgoing.setdefault(k,[]).append((j,p,q))
 assert all(len(v)==1 for v in outgoing.values()),'Ambiguous boundary junction'
 loops=[]
 while outgoing:
  start=next(iter(outgoing));k=start;loop=[]
  while True:
   assert k in outgoing,'Open boundary';j,p,q=outgoing.pop(k)[0];loop.append(p);k=j
   if k==start:break
  assert len(loop)>=3;loops.append(loop)
 return loops
