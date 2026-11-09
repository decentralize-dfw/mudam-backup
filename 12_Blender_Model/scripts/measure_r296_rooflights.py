import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
report=json.loads((R/'reports/R292_TWO_ROOFS.json').read_text());rows=[]
for light in report['rooflights']:
 p=np.array(light['polygon']);c=p.mean(axis=0);hs=[]
 for t in [0,.25,.5]:
  for q in p:
   xy=c*(1-t)+q*t;h,n,*_=tree.ray_cast(Vector((*xy,150)),Vector((0,0,-1)),200)
   if h:hs.append(h.z)
 d=dict(pixel=light['sourcePixel'],median=float(np.median(hs)),p10=float(np.percentile(hs,10)),p90=float(np.percentile(hs,90)),samples=len(hs));rows.append(d)
(R/'config/r296_rooflight_heights.json').write_text(json.dumps(rows,indent=2));print(rows,flush=True)
