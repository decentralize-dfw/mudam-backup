from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/bridge_full_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);d=json.loads((R/'reports/R175_BRIDGE_MEASUREMENTS.json').read_text());a=np.array(d['a']);u=np.array(d['u']);n=np.array(d['n']);hits=[]
for lo,hi in [(46,61),(64.6,77.8),(82.4,94.6),(101.6,116.2),(119.4,134.2),(137.6,152.2)]:
 station=(lo+hi)/2;valid=[]
 for z in np.arange(-55,-45,.05):
  p=a+u*station+n*20;h,no,*_=bvh.ray_cast(Vector((*p,z)),Vector((*(-n),0)),40)
  if h is not None and abs(np.dot(np.array(h[:2])-a-u*station,n)-5.2)<.65 and abs(no.x*n[0]+no.y*n[1])>.65:valid.append(float(z))
 hits.append(dict(lo=lo,hi=hi,center=station,wallMinimum=min(valid) if valid else None,samples=len(valid)))
(R/'config/r305_arch_crowns.json').write_text(json.dumps(hits,indent=2));print(hits)
