from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
# Independently traced visible raised roof divisions in the 1600px display of
# R190_roofs_source_top.png. The source mesh remains measurement-only.
traces=[[(1146,633),(1258,902)],[(1053,704),(1101,778)],[(1101,778),(1226,699)],[(1180,710),(1308,629)],[(1213,790),(1339,711)],[(1237,849),(1366,773)],[(1095,815),(1210,745)],[(1132,874),(1235,810)]]
out=[]
for index,(pa,pb) in enumerate(traces):
 a=Vector((255+pa[0]*.1125,525-pa[1]*.1125));b=Vector((255+pb[0]*.1125,525-pb[1]*.1125));u=(b-a).normalized();n=Vector((-u.y,u.x));samples=[]
 for t in np.linspace(.08,.92,max(8,int((b-a).length*2))):
  p=a.lerp(b,float(t));cross=[]
  for d in np.linspace(-.55,.55,9):
   q=p+n*float(d);h,nn,*_=g.ray_cast(Vector((q.x,q.y,40)),Vector((0,0,-1)),50)
   if h and 16.35<h.z<19.5:cross.append(float(h.z))
  if cross:samples.append(float(np.quantile(cross,.8)))
 out.append(dict(index=index,pixel_trace=[pa,pb],a=list(a),b=list(b),top=float(np.median(samples)) if samples else None,support=len(samples),samples=samples,width=.45,width_status='visual approximate; not surveyed'))
(R/'config/r209_roof_divisions.json').write_text(json.dumps(out,indent=2))
print([(r['index'],r['top'],r['support']) for r in out],flush=True)
