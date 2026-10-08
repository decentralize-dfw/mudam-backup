"""Convex planar clipping and inset helpers, independent of Blender."""
import math
def clip(poly,axis,value,sign):
 result=[]
 if not poly:return result
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=sign*(a[axis]-value);db=sign*(b[axis]-value);ina=da>=-1e-8;inb=db>=-1e-8
  if ina:result.append(a)
  if ina!=inb:
   t=da/(da-db);result.append([a[j]+t*(b[j]-a[j]) for j in range(2)])
 clean=[]
 for p in result:
  if not clean or math.dist(clean[-1],p)>1e-7:clean.append(p)
 if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-7:clean.pop()
 return clean
def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))/2
def inset(poly,gap):
 # Convex offset by clipping inward against each original edge.
 signed=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]));p=poly if signed>0 else list(reversed(poly));q=p[:]
 for a,b in zip(p,p[1:]+p[:1]):
  dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);n=(-dy/length,dx/length);c=n[0]*a[0]+n[1]*a[1]+gap;result=[]
  for u,v in zip(q,q[1:]+q[:1]):
   du=n[0]*u[0]+n[1]*u[1]-c;dv=n[0]*v[0]+n[1]*v[1]-c
   if du>=0:result.append(u)
   if (du>=0)!=(dv>=0):
    t=du/(du-dv);result.append([u[j]+t*(v[j]-u[j]) for j in range(2)])
  q=result
  if len(q)<3:return []
 return q
