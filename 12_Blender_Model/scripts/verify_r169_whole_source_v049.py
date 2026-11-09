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
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));source=tree();bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_KAYNAK_CATI_ADAY_v049.blend'));model=tree();q=np.array(json.loads((D/'row_whole_roof_samples_v045.json').read_text())['ring']);err=[];missing=0;worst=[]
for u in np.linspace(.013,.987,47):
 for v in np.linspace(.009,.991,71):
  p=(1-v)*((1-u)*q[0]+u*q[1])+v*((1-u)*q[3]+u*q[2]);a,*_=source.ray_cast(Vector((*p,50)),Vector((0,0,-1)),200);b,*_=model.ray_cast(Vector((*p,50)),Vector((0,0,-1)),200)
  if a is None or b is None:missing+=1;continue
  e=abs(a.z-b.z);err.append(e);worst.append((e,list(a),list(b)))
r=dict(independent_checks=len(err),missing=missing,p50_m=float(np.percentile(err,50)),p90_m=float(np.percentile(err,90)),p95_m=float(np.percentile(err,95)),max_m=max(err),worst=sorted(worst,reverse=True)[:10],accepted=False,published=False);(R/'reports/R169_WHOLE_SOURCE_v049.json').write_text(json.dumps(r,indent=2));print(r)
