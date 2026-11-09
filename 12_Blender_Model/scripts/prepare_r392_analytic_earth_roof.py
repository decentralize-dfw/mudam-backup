from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from shapely.geometry import Polygon,Point,box
from shapely.ops import triangulate
r=json.loads((R/'reports/R388_EARTH_PROFILE.json').read_text());arms=json.loads((R/'reports/R390_STRUCTURAL_ROOF_ZONES.json').read_text());heads=json.loads((R/'reports/R391_EAVE_PROFILE.json').read_text());outer=Polygon(r['outline']);inner=Polygon(r['inner']);domain=outer.difference(inner).intersection(Polygon([(-150,50),(50,50),(50,-150)]))
# This clipping half-plane is x+y >= -100; only the separately unresolved
# tower-end cover remains outside the independent analytic reconstruction.
assert all(arms[k]['valid'] for k in ['west_arm','east_arm']) and all(v['valid'] for v in heads.values())
def smooth(v):v=max(0,min(1,v));return v*v*(3-2*v)
def zfun(x,y):
 pt=Point(x,y);di=pt.distance(inner.boundary);do=pt.distance(outer.boundary)
 def arm(k):c=arms[k]['coef'];return c[0]+c[1]*di-c[2]*math.exp(-do/c[3])
 def head(k):c=heads[k]['coef'];return max(c[5],c[0]+c[1]*di-c[2]*math.exp(-max(0,do-c[4])/c[3]))
 w=smooth((y-x-5.5));z=arm('east_arm')*(1-w)+arm('west_arm')*w
 w=smooth((x+22.5));z=z*(1-w)+head('east_head')*w
 w=smooth((y+14.5));return z*(1-w)+head('north_head')*w
q=np.array(r['samples']);q=q[q[:,0]+q[:,1]>-100];cc=np.floor(q[:,:2]/.5).astype(int);q=q[(cc[:,0]+3*cc[:,1])%4==0];err=np.array([zfun(x,y)-z for x,y,z in q]);check=dict(rms=float(np.sqrt(np.mean(err**2))),max=float(abs(err).max()),heldout=len(q),valid=bool(np.sqrt(np.mean(err**2))<.1 and abs(err).max()<.25));print('COMPOSITE',check)
verts=[];faces=[];lookup={}
def index(x,y):
 key=(round(x,6),round(y,6))
 if key not in lookup:lookup[key]=len(verts);verts.append([key[0],key[1],zfun(*key)])
 return lookup[key]
x0,y0,x1,y1=domain.bounds
for x in np.arange(math.floor(x0*2)/2,x1,.5):
 for y in np.arange(math.floor(y0*2)/2,y1,.5):
  cut=domain.intersection(box(x,y,x+.5,y+.5))
  if cut.is_empty or cut.area<1e-9:continue
  for tri in triangulate(cut):
   if tri.area>1e-9 and cut.covers(tri.representative_point()):faces.append([index(a,b) for a,b in list(tri.exterior.coords)[:3]])
# Standing metal seams are authored strips at estimated 0.55m spacing,
# referenced from R336; no scanned photo is mapped onto the metal roof.
data=dict(vertices=verts,faces=faces,domain=list(domain.exterior.coords),holes=[list(h.coords) for h in domain.interiors],check=check,profiles=dict(arms=arms,heads=heads),method='Independent analytic architectural shoulder profiles on a regular half-metre tessellation; no source vertices, faces or textures transferred.',limits=['Tower-end cover below x+y=-100 retained pending independent junction reconstruction','Seam spacing is visual estimate, not measured survey'])
# Existing exterior wall top vertices receive the SAME analytic eave function
# when in this reconstructed domain, preventing a higher old masonry lip.
data['wallProfile']=[[x,y,zfun(x,y)] for x,y in r['outline'] if x+y>=-100]
(R/'reports/R392_ANALYTIC_EARTH_ROOF.json').write_text(json.dumps(data,separators=(',',':')));print('GEOMETRY',len(verts),len(faces),domain.is_valid)
