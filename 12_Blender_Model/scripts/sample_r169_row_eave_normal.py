from pathlib import Path
import bpy,json,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'roof_planes_164179202.json').read_text());ang=float(np.load(D/'164179202.npz')['angle']);cs,sn=math.cos(ang),math.sin(ang);planes=[p['coeff'] for p in d['planes'][:3]]
pixels=[(350,242),(857,120),(1014,778),(450,903)];ring=[Vector((-67+(x-700)*20/1400,-299+(550-y)*20/1400,0)) for x,y in pixels]
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[];center=sum(ring,Vector())/4
for edge in range(4):
 for j in range(11):
  p=ring[edge].lerp(ring[(edge+1)%4],j/10);edge_t=(ring[(edge+1)%4]-ring[edge]).normalized();toward=Vector((edge_t.y,-edge_t.x,0));toward= toward if (center-p).dot(toward)>0 else -toward
  for inset in [0,.25,.5,1.]:
   q=p+toward*inset;hit,*_=tree.ray_cast(Vector((q.x,q.y,50)),Vector((0,0,-1)),200)
   x,y=cs*q.x+sn*q.y,-sn*q.x+cs*q.y;h=min(a*x+b*y+c for a,b,c in planes)
   rows.append(dict(edge=edge,t=j/10,inset=inset,x=q.x,y=q.y,plane=h,source=None if hit is None else hit.z,delta=None if hit is None else hit.z-h))
(D/'row_eave_normal_samples.json').write_text(json.dumps(rows,indent=2));print('EAVE_SAMPLES',json.dumps([r for r in rows if r['edge']==2 and r['inset'] in [0,1.]],indent=1),flush=True)
