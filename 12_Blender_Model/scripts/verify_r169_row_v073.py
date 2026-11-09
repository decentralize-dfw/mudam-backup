from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169'
def tree():
 vs=[];fs=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
 return BVHTree.FromPolygons(vs,fs,all_triangles=True)
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));source=tree();bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v073.blend'));model=tree();d=json.loads((D/'row_whole_roof_samples_v061.json').read_text());vs=np.array(d['vertices']);nx=d['nx'];ny=d['ny'];err=[];worst=[];missing=0
for j in range(ny-1):
 for i in range(nx-1):
  k=j*nx+i;p=(vs[k]+vs[k+1]+vs[k+nx]+vs[k+nx+1])*.25;a,*_=source.ray_cast(Vector((p[0],p[1],50)),Vector((0,0,-1)),200);b,*_=model.ray_cast(Vector((p[0],p[1],50)),Vector((0,0,-1)),200)
  if a is None or b is None:missing+=1;continue
  err.append(abs(a.z-b.z));worst.append((abs(a.z-b.z),list(a),list(b)))
r=dict(scope='Whole four-house roof only; independent cell-centre source rays. Not facade or entire environment similarity.',checks=len(err),worst=sorted(worst,reverse=True)[:12],missing=missing,within10cm_percent=float(np.mean(np.array(err)<=.1)*100),p90_m=float(np.percentile(err,90)),p95_m=float(np.percentile(err,95)),max_m=max(err),accepted=False,published=False);(R/'reports/R169_WHOLE_ROW_GEOMETRY_v073.json').write_text(json.dumps(r,indent=2));print(r)

