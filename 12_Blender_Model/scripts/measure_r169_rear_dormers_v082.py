from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r169/source.blend'));v=[];f=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(v);v.extend(o.matrix_world@p.co for p in o.data.vertices);f.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(v,f,all_triangles=True);center=Vector((-81.746925354,-294.516082764,-69));right=Vector((-.97769629955,-.2100233883,0));n=Vector((-.2100236565,.97769629955,0));records=[]
for x in [130,150,170,345,370,395,1310,1335,1360,1570,1595,1620,1720,1740,1760]:
 for y in [125,140,155]:
  p=center+right*((x-1024)*36/2048);p.z=-69+(395.636-y)*36/2048;h,norm,idx,dist=tree.ray_cast(p+n*3,-n,7)
  if h:records.append(dict(pixel=[x,y],point=list(h),offset=(h-p).dot(n),normal=list(norm)))
(R/'.local_source_cache/r169/rear_dormer_measurements_v082.json').write_text(json.dumps(records,indent=2))
for y in [125,140,155]:
 a=[r['offset'] for r in records if r['pixel'][1]==y];print('HEIGHT',-69+(395.636-y)*36/2048,'offset median',float(np.median(a)),'minmax',min(a),max(a))
print('SAMPLES',len(records))
