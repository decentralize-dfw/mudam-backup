from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
parts=json.loads((R/'config/r215_erasmus_roof_traces.json').read_text())['parts']+[dict(p,id=10+p['offset'])for p in json.loads((R/'config/r217_additional_wing_measurements.json').read_text())['candidates']if p['supported']];parts.sort(key=lambda r:r['polygon'][0][0]);rows=[]
for i,(a,b) in enumerate(zip(parts,parts[1:])):
 p=np.array(a['polygon']);q=np.array(b['polygon']);v=p[3]-p[0];v/=np.linalg.norm(v);poly=np.array([p[1]+v,q[0]+v,q[0]-v*4,p[1]-v*4]);zs=[]
 for u in np.linspace(.15,.85,13):
  for w in np.linspace(.15,.85,9):
   xy=poly[0]+u*(poly[1]-poly[0])+w*(poly[3]-poly[0]);h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
   if h and n.z>.85:zs.append(float(h.z))
 if not zs:continue
 med=float(np.median(zs));p90=float(np.percentile(abs(np.array(zs)-med),90));rows.append(dict(id=i,polygon=poly.tolist(),roof=med,p90=p90,samples=len(zs),supported=len(zs)>90 and p90<.2,between=[a['id'],b['id']]))
(R/'config/r220_rear_connectors.json').write_text(json.dumps(dict(parts=rows,limits='4m rear-strip depth is visual candidate; scalar source elevations only, not source mesh'),indent=2));print(rows,flush=True)

