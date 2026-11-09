import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
b=BVHTree.FromPolygons(vs,fs,all_triangles=True)
import numpy as np
stations=json.loads((R/'reports/R321_WEST_WALL_STATIONS.json').read_text())['source'];rows=[]
for st in stations:
 x,y=st['xy'];hits=[]
 for dx in np.linspace(-1.2,1.2,9):
  for dy in np.linspace(-1.2,1.2,9):
   h,n,idx,d=b.ray_cast(Vector((x+dx,y+dy,100)),Vector((0,0,-1)),200)
   if h and abs(n.z)>.55 and h.z<.5:hits.append(list(h))
 if not hits:raise RuntimeError(st['name'])
 hits=np.array(hits);cut=np.quantile(hits[:,2],.85);upper=hits[hits[:,2]>=cut];center=np.median(upper,axis=0)
 rows.append(dict(name=st['name'],traceXY=st['xy'],measuredCrest=center.tolist(),range=[float(min(hits[:,2])),float(max(hits[:,2]))],horizontalSamples=len(hits)))
(R/'reports/R321_WEST_CREST_MEASUREMENTS.json').write_text(json.dumps(rows,indent=2));print([(x['name'],x['measuredCrest']) for x in rows])
