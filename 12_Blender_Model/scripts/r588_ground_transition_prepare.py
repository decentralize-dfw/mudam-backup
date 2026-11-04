import json,sys,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];W=R/'reports'
CACHE=R/'.local_source_cache/r588_ground'
CACHE.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,Point,box,LineString
from shapely.ops import split
from shapely import constrained_delaunay_triangles
from shapely.strtree import STRtree
D=json.loads((CACHE/'R588_GROUND_FULL_INPUT.json').read_text());A=json.loads((W/'R588_GROUND_GRADE_CONTINUITY.json').read_text());S=json.loads((W/'R588_R523_SOURCE_GRADE_AUDIT.json').read_text())
ROI=box(-33,-9.55,-24,3.8)
lower=np.array(S['core']['plane']);west=np.array(S['upperSlopePlanes'][0]['plane']);east=np.array(S['upperSlopePlanes'][1]['plane'])
breaks=np.array(S['recommendedDomain']['class2BoundaryCandidateNotExact'])
def boundary(x):
 if x<breaks[0,0]:return breaks[0,1]+(x-breaks[0,0])*(breaks[1,1]-breaks[0,1])/(breaks[1,0]-breaks[0,0])
 return float(np.interp(x,breaks[:,0],breaks[:,1]))
def smooth(t):
 t=max(0,min(1,float(t)));return t*t*(3-2*t)
def grade(x,y,old):
 if not(-33<=x<=-24 and -9.55<=y<=3.8):return old
 # Only the independently supported visible floor is fully corrected. South
 # feather lies at the protected building edge; no ground survey claim there.
 w=smooth(min(x+33,-24-x,y+9.55,3.8-y)/1.2)
 lo=float(np.dot(lower,[x,y,1]));t=smooth((x+31.5))
 hi=float((1-t)*np.dot(west,[x,y,1])+t*np.dot(east,[x,y,1]))
 g=smooth((y-boundary(x)+.06)/.12);target=lo*(1-g)+hi*g
 return old+w*(target-old)
cells=[]
for x in np.arange(-33,-24,.5):
 for y in np.arange(-9.55,3.8,.5):
  p=box(x,y,min(x+.5,-24),min(y+.5,3.8))
  pieces=[p]
  for off in [-.06,0,.06]:
   line=LineString([(q,boundary(q)+off)for q in [-34,*breaks[:,0].tolist(),-23]])
   nxt=[]
   for a in pieces:
    nxt.extend(list(split(a,line).geoms))
   pieces=nxt
  cells.extend([a for a in pieces if a.area>1e-10])
ct=STRtree(cells)
def polygons(g):
 if g.geom_type=='Polygon':return [g]
 if hasattr(g,'geoms'):return [p for h in g.geoms for p in polygons(h)]
 return []
def triangulate(g):
 return [np.array(t.exterior.coords)[:3]for p in polygons(g)if p.area>1e-11 for t in constrained_delaunay_triangles(p).geoms if t.area>1e-11]
def modify_top(o,override=None,terrain=False):
 v=np.array(o['vertices']);out=[];changed=0;maxdelta=0
 for ti,t in enumerate(o['triangles']):
  if t['normal'][2]<.05:
   if terrain:out.append(dict(v=v[t['vertices']].tolist(),uv={name:[ar[i]for i in t['loops']]for name,ar in o['uv'].items()},normals=[o['normals'][i]for i in t['loops']],source=ti,material=t['material'],inside=False))
   continue
  a=v[t['vertices']].copy()
  if override:
   for j,p in enumerate(a):
    key=(round(p[0],6),round(p[1],6));a[j,2]=override.get(key,p[2])
  p=Polygon(a[:,:2]);det=np.linalg.det(np.c_[a[:,:2],np.ones(3)])
  if abs(det)<1e-12:continue
  inv=np.linalg.inv(np.c_[a[:,:2],np.ones(3)].T)
  n=np.array([o['normals'][i]for i in t['loops']]);uv={name:np.array([ar[i]for i in t['loops']])for name,ar in o['uv'].items()}
  pieces=[]
  if p.intersects(ROI) and p.intersection(ROI).area>1e-10:
   changed+=1
   pieces+=triangulate(p.difference(ROI))
   for ci in ct.query(p):pieces+=triangulate(p.intersection(cells[int(ci)]))
  else:pieces=[a[:,:2]]
  for xy in pieces:
   weights=np.c_[xy,np.ones(3)]@inv.T;oldz=weights@a[:,2]
   z=np.array([grade(x,y,q)for(x,y),q in zip(xy,oldz)])
   maxdelta=max(maxdelta,float(np.max(np.abs(z-oldz))))
   xyz=np.c_[xy,z]
   if np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0])[2]<0:
    xyz=xyz[[0,2,1]];weights=weights[[0,2,1]]
   norms=weights@n;norms/=np.maximum(np.linalg.norm(norms,axis=1)[:,None],1e-10)
   out.append(dict(v=xyz.tolist(),uv={k:(weights@q).tolist()for k,q in uv.items()},normals=norms.tolist(),source=ti,material=t['material'],inside=bool(p.intersects(ROI))))
 return out,dict(changedOriginalTriangles=changed,maxGradeDelta=maxdelta,topTriangles=len(out))
# A's common-boundary height offsets are interpolated through the complete patch.
av=np.array(A['vertices']);override={}
for x,y in np.unique(av[:,:2],axis=0):override[(round(x,6),round(y,6))]=float(max(av[(av[:,0]==x)&(av[:,1]==y),2]))
result={};reports={}
for name in ['R152_CLASS2_TERRAIN','R523_WEST_MOAT_LOWER_GROUND_0','R588_WEST_CLASS2_GROUND_RESTORATION']:
 result[name],reports[name]=modify_top(D[name],override if name.startswith('R588_')else None,terrain=name=='R152_CLASS2_TERRAIN')
(CACHE/'R588_GROUND_TRANSITION_DATA.json').write_text(json.dumps(dict(objects=result,reports=reports,ROI=list(ROI.bounds),breakCandidate=breaks.tolist(),source=str(W/'R588_R523_SOURCE_GRADE_AUDIT.json'),limits=S['limits'],method='Independent lower/upper grade planes with a 0.12m steep connector along measured diagonal break; preserve current outer grade through bounded C1 feather. No scan surface or image copied.'),separators=(',',':')))
print(reports)
