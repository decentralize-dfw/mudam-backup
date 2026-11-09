import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];points=json.loads((R/'reports/R372_EAST_MUSEUM_MOAT_LEVELS.json').read_text());result={}
for label,path in [('source',R/'.local_source_cache/r316/museum_ring_reference.blend'),('model',R/'scenes/MUDAM_R378_DOGU_UZUN_HENDEK_ZEMIN_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));vs=[];fs=[];names=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render:continue
  o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles);names.extend([o.name]*len(o.data.loop_triangles))
 bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]
 for row in points:
  x,y=row['xy'];h,n,i,d=bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200);rows.append(dict(xy=[x,y],z=h.z if h else None,object=names[i] if h else None))
 result[label]=rows
(R/'reports/R379_EAST_GROUND_SOURCE_COMPARE.json').write_text(json.dumps(result,indent=2));print(result)
