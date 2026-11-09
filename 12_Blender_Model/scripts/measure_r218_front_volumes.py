from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
parts=json.loads((R/'config/r215_erasmus_roof_traces.json').read_text())['parts']+[dict(p,id=10+p['offset'])for p in json.loads((R/'config/r217_additional_wing_measurements.json').read_text())['candidates']if p['supported']]
rows=[]
for r in parts:
 p=np.array(r['polygon']);v=(p[3]-p[0]);v/=np.linalg.norm(v)
 # Lower street-facing roof spans are visible in R214 module source; 7m extension is a traced candidate.
 poly=np.array([p[3],p[2],p[2]+v*7,p[3]+v*7]);zs=[]
 for a in np.linspace(.18,.82,9):
  for b in np.linspace(.18,.82,9):
   xy=poly[0]+a*(poly[1]-poly[0])+b*(poly[3]-poly[0]);h,n,*_=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)
   if h and n.z>.85:zs.append(float(h.z))
 if len(zs)<40:continue
 z=float(np.median(zs));res=float(np.percentile(abs(np.array(zs)-z),90));rows.append(dict(id=r['id'],polygon=poly.tolist(),roof=z,p90=res,samples=len(zs),supported=res<.2 and 6<z<11))
(R/'config/r218_front_volumes_measured.json').write_text(json.dumps(dict(parts=rows,limits='Footprint extensions are visual candidates; no survey precision claimed'),indent=2));print(rows,flush=True)
