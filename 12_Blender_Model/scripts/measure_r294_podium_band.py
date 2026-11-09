import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);a=Vector((189.375,24.375));b=Vector((302.25,95.25));u=(b-a).normalized();n=Vector((u.y,-u.x));rows=[]
for t in np.linspace(.04,.96,160):
 for z in [19.5,20,20.5,21,21.5]:
  p=a+(b-a)*t;ray=Vector((*(p+n*7),z));h,normal,*_=tree.ray_cast(ray,Vector((-n.x,-n.y,0)),10)
  if h and abs(Vector((normal.x,normal.y)).dot(n))>.65:
   offset=(Vector(h.xy)-p).dot(n);rows.append(dict(t=float(t),z=z,offset=offset))
offsets=np.array([r['offset'] for r in rows]);median=float(np.median(offsets));err=abs(offsets-median)
d=dict(start=list(a),end=list(b),outward=list(n),count=len(rows),medianOffset=median,p90=float(np.percentile(err,90)),samples=rows,scope='Source-visible upper facade only; vegetation and hidden lower walls unresolved')
(R/'config/r294_podium_band.json').write_text(json.dumps(d,indent=2));print({k:v for k,v in d.items() if k!='samples'},flush=True)
