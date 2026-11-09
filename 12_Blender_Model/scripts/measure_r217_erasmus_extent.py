from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);base=np.array(json.loads((R/'config/r215_erasmus_roof_traces.json').read_text())['parts'][0]['polygon']);rows=[]
# Search measured recurring roof spans; phase and endpoints remain source-checked candidates.
for offset in [-2,2,3,4,5]:
 best=None
 for delta in np.arange(-1,1.01,.25):
  p=base+np.array([18.15,15.65])*(offset+delta/24);zs=[]
  for a in np.linspace(.15,.85,7):
   for b in np.linspace(.15,.85,11):
    xy=p[0]+a*(p[1]-p[0])+b*(p[3]-p[0]);h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
    if h and n.z>.85:zs.append(float(h.z))
  if len(zs)<60:continue
  med=float(np.median(zs));res=float(np.percentile(abs(np.array(zs)-med),90));score=res+abs(med-11.42)*.1
  if best is None or score<best['score']:best=dict(offset=offset,phaseAdjustmentMeters=float(delta),polygon=p.tolist(),roof=med,p90=res,samples=len(zs),score=score)
 if best:best['supported']=best['p90']<.15 and 11<best['roof']<12;rows.append(best)
(R/'config/r217_additional_wing_measurements.json').write_text(json.dumps(dict(candidates=rows,method='Parametric repeated spans tested against independent scalar roof samples; no source faces copied'),indent=2));print(rows,flush=True)
