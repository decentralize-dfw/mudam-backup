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
rows=[]
for sx in [350,500,650]:
 line=[]
 for sy in range(80,551,4):
  x=-57+sx*44/1200;y=84.5-sy*44/1200
  h,n,idx,d=b.ray_cast(Vector((x,y,50)),Vector((0,0,-1)),100)
  if h:line.append(dict(screen=[sx,sy],xyz=list(h),nz=n.z))
 rows.append(line)
(R/'reports/R328_NORTH_MOAT_SECTIONS.json').write_text(json.dumps(rows,indent=2));print('R328_SECTIONS_READY')
