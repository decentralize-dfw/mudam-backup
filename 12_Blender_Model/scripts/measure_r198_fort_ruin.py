from pathlib import Path
import json,bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
pixels=[(625,902),(660,850),(733,911),(699,959)];xy=[Vector((-340+x*.1625,-45-y*.1625)) for x,y in pixels];edges=[]
for a,b in zip(xy,xy[1:]+xy[:1]):
 n=Vector((-(b-a).y,(b-a).x)).normalized();samples=[]
 for t in [.15,.35,.5,.65,.85]:
  p=a.lerp(b,t);cross=[]
  for offset in [-.6,-.3,0,.3,.6]:
   q=p+n*offset;h,normal,*_=g.ray_cast(Vector((q.x,q.y,100)),Vector((0,0,-1)),300)
   if h:cross.append([offset,h.z,normal.z])
  samples.append(cross)
 edges.append(dict(a=list(a),b=list(b),samples=samples))
center=sum(xy,Vector((0,0)))/4;floor=[]
for dx,dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]:
 h,*_=g.ray_cast(Vector((center.x+dx,center.y+dy,100)),Vector((0,0,-1)),300)
 if h:floor.append(list(h))
(R/'reports/R198_RUIN_MEASUREMENTS.json').write_text(json.dumps(dict(pixels=pixels,xy=[list(p) for p in xy],edges=edges,floor=floor),indent=2));print('FLOOR',floor,flush=True)
