"""Remove only tiny crossing loops at source podium ink/curved-wall closures."""
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def area(poly):return abs(sum(cross2(a,b) for a,b in zip(poly,poly[1:]+poly[:1]))/2)
def crossings(points):
 for i in range(len(points)):
  for j in range(i+2,len(points)):
   if i==0 and j==len(points)-1:continue
   a,b,c,d=points[i],points[(i+1)%len(points)],points[j],points[(j+1)%len(points)]
   u=[b[k]-a[k] for k in range(2)];v=[d[k]-c[k] for k in range(2)];w=[c[k]-a[k] for k in range(2)];den=cross2(u,v)
   if abs(den)<1e-12:continue
   t=cross2(w,v)/den;q=cross2(w,u)/den
   if 1e-8<t<1-1e-8 and 1e-8<q<1-1e-8:yield i,j,[a[k]+u[k]*t for k in range(2)]
def repair_closure(source):
 points=[list(p) for p in source];repairs=[]
 for attempt in range(10):
  crossing=next(crossings(points),None)
  if crossing is None:return points,repairs
  i,j,hit=crossing;loops=[points[i+1:j+1]+[hit],points[j+1:]+points[:i+1]+[hit]];loops.sort(key=area,reverse=True);removed=area(loops[1])
  assert removed<1,('Large source crossing needs independent review',removed)
  repairs.append(dict(edges=[i,j],intersection_canonical=hit,removed_loop_area_canonical_px2=removed));points=loops[0]
 raise RuntimeError('Source closure did not converge')
