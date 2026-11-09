from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
domains=[('UPPER_ENTRANCE',[(695,350),(713,373),(782,398),(827,420),(875,480),(1009,616),(1040,634),(1074,638),(1117,613),(1179,557),(1212,605),(1170,670),(1107,720),(1064,728),(1018,722),(977,699),(947,664),(916,648),(881,649),(843,670),(794,711),(741,762),(701,737),(812,626),(840,601),(851,577),(847,552),(830,517),(808,489),(779,469),(741,457),(695,446),(654,443)]),('DIAGONAL_ACCESS',[(741,762),(794,711),(701,815),(638,889),(580,964),(537,948),(585,885),(627,829),(683,780),(701,737)]),('SOUTH_LOOP',[(580,964),(600,1022),(599,1054),(618,1079),(644,1087),(664,1077),(695,1054),(740,1028),(778,1043),(783,1092),(759,1126),(722,1147),(677,1160),(627,1158),(582,1140),(550,1116),(533,1081),(526,1039),(532,993),(537,948)])]
def inside(x,y,ring):
 h=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:h=not h
 return h
white_pixels=[(562,1115),(595,1080),(640,1085),(680,1054),(740,1028),(778,1043),(783,1092),(759,1126),(722,1147),(677,1160),(627,1158),(582,1140)]
white_xy=[(-85+x*.1,490-y*.1) for x,y in white_pixels]
domains.append(('SOUTH_CONCRETE_TERRACE',white_pixels))
out=[];rng=np.random.default_rng(213)
for name,pix in domains:
 xy=[(-85+x*.1,490-y*.1) for x,y in pix];samples=[]
 for x in np.arange(min(p[0] for p in xy),max(p[0] for p in xy),.65):
  for y in np.arange(min(p[1] for p in xy),max(p[1] for p in xy),.65):
   if not inside(x,y,xy) or (name=='SOUTH_LOOP' and inside(x,y,white_xy)):continue
   p,n,*_=g.ray_cast(Vector((x,y,50)),Vector((0,0,-1)),100)
   if p and n.z>.85:samples.append([x,y,p.z])
 a=np.array(samples);origin=a[:,:2].mean(0);X=np.c_[a[:,:2]-origin,np.ones(len(a))];best=None
 for _ in range(300):
  ids=rng.choice(len(a),3,replace=False)
  try:c=np.linalg.solve(X[ids],a[ids,2])
  except np.linalg.LinAlgError:continue
  residual=np.abs(X@c-a[:,2]);mask=residual<.22
  if best is None or mask.sum()>best.sum():best=mask
 c=np.linalg.lstsq(X[best],a[best,2],rcond=None)[0];res=np.abs(X@c-a[:,2]);out.append(dict(name=name,xy=xy,pixels=pix,origin=origin.tolist(),plane=c.tolist(),measurements=samples,samples=len(a),inliers=int(best.sum()),support=float(best.mean()),p90=float(np.quantile(res[best],.9)),all_p90=float(np.quantile(res,.9))))
(R/'config/r213_access_measured.json').write_text(json.dumps(out,indent=2));print(out)
