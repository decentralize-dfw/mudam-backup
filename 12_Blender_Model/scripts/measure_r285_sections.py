from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]


a=np.array([688.,273.]);end=np.array([215.,1020.]);across=np.array([212.,124.]);out=[]
for t in np.linspace(0,1,301):
 heights=[]
 for u in np.linspace(.2,.8,9):
  p=a+(end-a)*t+across*u;xy=[290+p[0]/12,285-p[1]/12];h,n,*_=g.ray_cast(Vector((*xy,200)),Vector((0,0,-1)),300)
  heights.append(float(h.z) if h else None)
 valid=[z for z in heights if z is not None];out.append(dict(t=float(t),distance=float(np.linalg.norm(end-a)/12*t),heights=heights,median=float(np.median(valid)),lo=float(np.percentile(valid,10)),hi=float(np.percentile(valid,90))))
(R/'config/r285_north_roof_sections.json').write_text(json.dumps(out,indent=2));print([(round(r['distance'],1),round(r['median'],2),round(r['hi']-r['lo'],2)) for r in out[::5]],flush=True)
