from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
b=BVHTree.FromPolygons(vs,fs,all_triangles=True);d=json.loads((R/'config/r302_fort_surfaces.json').read_text());out=[]
for x,y in d['eastOuter']:
 zs=[]
 for dx in np.linspace(-1.5,1.5,9):
  for dy in np.linspace(-1.5,1.5,9):
   h,n,*_=b.ray_cast(Vector((x+dx,y+dy,100)),Vector((0,0,-1)),300)
   if h and h.z<-5 and abs(n.z)>.5:zs.append(h.z)
 out.append(dict(x=x,y=y,n=len(zs),p25=float(np.quantile(zs,.25)) if zs else None,median=float(np.median(zs)) if zs else None))
d['outerHeightStudy']=out;(R/'config/r302_fort_surfaces.json').write_text(json.dumps(d,indent=2));print(out)
