from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=json.loads((R/'config/r176_authored_parts.json').read_text());out=[]
def inside(p,ring):
 h=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:h=not h
 return h
for r in rows:
 if r['name'] not in ['NOVOTEL_LOW','NOVOTEL_HIGH']:continue
 xy=r['outer'];samples=[]
 for x in np.arange(min(p[0] for p in xy),max(p[0] for p in xy),1):
  for y in np.arange(min(p[1] for p in xy),max(p[1] for p in xy),1):
   if not inside((x,y),xy) or any(inside((x,y),h) for h in r['holes']):continue
   h,n,*_=g.ray_cast(Vector((x,y,80)),Vector((0,0,-1)),150)
   if h and n.z>.9:samples.append([x,y,h.z])
 a=np.array(samples);bins,counts=np.unique(np.round(a[:,2]*5)/5,return_counts=True);modes=sorted(zip(bins.tolist(),counts.tolist()),key=lambda p:p[1],reverse=True)[:10];out.append(dict(name=r['name'],samples=samples,modes=modes))
(R/'reports/R203_INTERIOR_ROOF_LEVELS.json').write_text(json.dumps(out,indent=2));print([(r['name'],r['modes']) for r in out])
