from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]
a=np.array([178.3125,26.625]);b=np.array([332.4375,282.375]);L=np.linalg.norm(b-a);u=(b-a)/L;n=np.array([-u[1],u[0]])
for station in np.linspace(5,L-5,25):
 hits=[]
 for off in np.linspace(-8,2,41):
  xy=a+u*station+n*off;h,no,*_=g.ray_cast(Vector((*xy,130)),Vector((0,0,-1)),200)
  if h is not None and 10<h.z<30 and no.z>.7:hits.append([float(off),h.z])
 rows.append(dict(station=float(station),hits=hits))
(R/'config/r307_podium_edge_levels.json').write_text(json.dumps(dict(a=a.tolist(),b=b.tolist(),length=L,rows=rows),indent=2));print([(round(r['station']),len(r['hits']),round(float(np.median([v[1] for v in r['hits']])),2) if r['hits'] else None) for r in rows])
