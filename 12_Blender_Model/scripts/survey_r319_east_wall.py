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
b=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]
for py in [470,490,510,530,550,570,590,610,630,650,670]:
 line=[]
 for px in range(1080,1141):
  x=-120+px*220/1400;y=95-py*220/1400
  h,n,idx,d=b.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
  if h:line.append(dict(pixel=[px,py],xyz=list(h),normal=list(n)))
 rows.append(line)
(R/'reports/R319_EAST_WALL_SECTIONS.json').write_text(json.dumps(rows,indent=2))
print('R319_SECTIONS_READY')
