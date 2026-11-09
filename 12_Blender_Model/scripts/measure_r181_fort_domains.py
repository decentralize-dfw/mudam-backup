from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
domains=[('WEST_BASTION', [(444, 592), (659, 504), (744, 655), (690, 710), (604, 710), (478, 650)]), ('WEST_RAMPART', [(604, 736), (692, 729), (985, 1057), (971, 1074)]), ('SOUTHWEST_COURT', [(389, 866), (556, 798), (630, 869), (624, 931), (700, 970), (767, 920), (807, 953), (688, 1083), (558, 1128), (454, 1020)]), ('SOUTHEAST_BASTION', [(1026, 930), (1219, 1000), (1148, 1087), (1080, 1137), (930, 1160), (920, 1110), (977, 1080)]), ('TRIANGLE_COURT', [(893, 659), (1028, 640), (1041, 790), (974, 754)]), ('NORTH_COURT', [(783, 501), (931, 427), (941, 511), (1050, 523), (1054, 548), (841, 567)]), ('EAST_MOAT', [(1140, 619), (1173, 625), (1180, 808), (1140, 808)]), ('SOUTH_MOAT', [(1034, 851), (1201, 893), (1231, 965), (1055, 891), (978, 936), (937, 899)]), ('CENTRAL_COURT', [(807, 668), (869, 663), (910, 726), (868, 772), (844, 798), (763, 722)])]
def inside(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
out=[];rng=np.random.default_rng(172)
for name,pixels in domains:
 xy=[[-340+x*260/1600,-45-y*260/1600] for x,y in pixels];samples=[]
 for x in np.linspace(min(p[0] for p in xy),max(p[0] for p in xy),15)[1:-1]:
  for y in np.linspace(min(p[1] for p in xy),max(p[1] for p in xy),15)[1:-1]:
   if not inside((x,y),xy):continue
   h,n,*_=bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),300)
   if h and abs(n.z)>.85:samples.append([x,y,h.z])
 a=np.array(samples);origin=a[:,:2].mean(0);X=np.c_[a[:,:2]-origin,np.ones(len(a))];best=None
 for i in range(300):
  ix=rng.choice(len(a),3,replace=False)
  if abs(np.linalg.det(X[ix]))<.01:continue
  c=np.linalg.solve(X[ix],a[ix,2]);mask=abs(X@c-a[:,2])<.25
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(X[best],a[best,2],rcond=None)[0];err=abs(X@c-a[:,2]);support=float((err<.3).mean());out.append(dict(name=name,xy=xy,pixels=pixels,origin=origin.tolist(),plane=c.tolist(),samples=samples,support=support,p90=float(np.quantile(err,.9)),accepted=bool(support>.85 and np.linalg.norm(c[:2])<.35)))
(R/'reports/R181_FORT_DOMAINS.json').write_text(json.dumps(out,indent=2));print([(r['name'],r['support'],r['p90'],r['accepted']) for r in out])

