from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
out=[]
for name,pixels in [('CENTRAL_BRIDGE',[(855,812),(871,829),(947,763),(930,747)]),('RUIN_PARTITION',[(638,903),(710,946)])]:
 xy=[Vector((-340+x*.1625,-45-y*.1625)) for x,y in pixels];samples=[]
 if len(xy)==4:
  for u in np.linspace(.05,.95,10):
   for v in [.15,.35,.5,.65,.85]:
    p=xy[0].lerp(xy[3],u).lerp(xy[1].lerp(xy[2],u),v)
    h,n,*_=g.ray_cast(Vector((p.x,p.y,80)),Vector((0,0,-1)),200)
    if h:samples.append([*h,n.z])
 else:
  for u in np.linspace(.05,.95,12):
   p=xy[0].lerp(xy[1],u);h,n,*_=g.ray_cast(Vector((p.x,p.y,80)),Vector((0,0,-1)),200)
   if h:samples.append([*h,n.z])
 out.append(dict(name=name,pixels=pixels,xy=[list(p) for p in xy],samples=samples))
(R/'reports/R199_FORT_LINK_MEASUREMENTS.json').write_text(json.dumps(out,indent=2))
