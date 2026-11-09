from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r169/source.blend'));v=[];f=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(v);v.extend(o.matrix_world@p.co for p in o.data.vertices);f.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(v,f,all_triangles=True);center=Vector((-78.6563873,-306.0042725,-69));right=Vector((.9779602885,.2087912709,0));n=Vector((.208791494,-.977960169,0));records=[]
for x in [250,270,520,540,805,820,1010,1030,1505,1520,1725,1740]:
 for y in [105,120,140,160,180,195,210]:
  p=center+right*((x-1024)*36/2048);p.z=-69+(395.636-y)*36/2048;h,norm,idx,dist=tree.ray_cast(p+n*3,-n,7)
  if h:records.append(dict(pixel=[x,y],point=list(h),offset=(h-p).dot(n),normal=list(norm)))
(R/'.local_source_cache/r169/front_mansard_measurements_v078.json').write_text(json.dumps(records,indent=2))
for y in [105,120,140,160,180,195,210]:
 a=[r['offset'] for r in records if r['pixel'][1]==y];print('HEIGHT',-69+(395.636-y)*36/2048,'offset median',float(np.median(a)),'minmax',min(a),max(a))
print('SAMPLES',len(records))
