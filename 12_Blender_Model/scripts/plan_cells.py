"""Nonoverlapping trapezoids covering polygon minus exclusions, without hole n-gons."""
from plan_union import inside,cross,sub
def cells(outer,holes=()):
 polys=[outer]+list(holes);edges=[(a,b) for poly in polys for a,b in zip(poly,poly[1:]+poly[:1])];xs=[p[0] for poly in polys for p in poly]
 for i,(a,b) in enumerate(edges):
  v=sub(b,a)
  for c,d in edges[i+1:]:
   w=sub(d,c);den=cross(v,w)
   if abs(den)<1e-9:continue
   t=cross(sub(c,a),w)/den;u=cross(sub(c,a),v)/den
   if 0<t<1 and 0<u<1:xs.append(a[0]+v[0]*t)
 xs=sorted(set(round(x,7) for x in xs));result=[]
 for x0,x1 in zip(xs,xs[1:]):
  if x1-x0<1e-5:continue
  xm=(x0+x1)/2;crossing=[]
  for a,b in edges:
   if min(a[0],b[0])<xm<max(a[0],b[0]):
    def y(x):return a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0])
    crossing.append((y(xm),y(x0),y(x1)))
  crossing.sort()
  for lo,hi in zip(crossing,crossing[1:]):
   sample=(xm,(lo[0]+hi[0])/2)
   if hi[0]-lo[0]<1e-5 or not inside(sample,outer) or any(inside(sample,p) for p in holes):continue
   poly=[(x0,lo[1]),(x1,lo[2]),(x1,hi[2]),(x0,hi[1])];clean=[]
   for p in poly:
    if not clean or sum((a-b)**2 for a,b in zip(p,clean[-1]))>1e-10:clean.append(p)
   if len(clean)>2 and sum((a-b)**2 for a,b in zip(clean[0],clean[-1]))<1e-10:clean.pop()
   if len(clean)>=3:result.append(clean)
 return result
