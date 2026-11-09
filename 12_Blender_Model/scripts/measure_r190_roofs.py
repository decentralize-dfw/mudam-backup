from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
domains=[('MAMA_TERRACE',[(89,654),(314,511),(400,632),(155,753)]),('MAMA_WARM_ROOF',[(338,530),(453,450),(582,453),(634,491),(409,642)]),('MAMA_TECHNICAL',[(397,515),(467,469),(496,492),(431,540)]),('NOVOTEL_TECHNICAL',[(1004,597),(1058,571),(1098,636),(1043,659)])]
def inside(p,poly):
 h=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:h=not h
 return h
out=[]
for name,pix in domains:
 xy=[(255+x*.1125,525-y*.1125) for x,y in pix];samples=[]
 for x in np.linspace(min(p[0] for p in xy),max(p[0] for p in xy),11)[1:-1]:
  for y in np.linspace(min(p[1] for p in xy),max(p[1] for p in xy),11)[1:-1]:
   if not inside((x,y),xy):continue
   h,n,*_=bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
   if h and n.z>.8:samples.append(float(h.z))
 out.append(dict(name=name,xy=xy,pixels=pix,source='R190 top orthographic180m at345,435; traced in1600px display',samples=samples,median=float(np.median(samples)),p10=float(np.quantile(samples,.1)),p90=float(np.quantile(samples,.9))))
(R/'config/r190_roof_measurements.json').write_text(json.dumps(out,indent=2));print([(r['name'],r['median'],r['p10'],r['p90']) for r in out])
