import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def tree():
 vs=[];fs=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or o.name.startswith('R158_TREE_'):continue
  bb=[o.matrix_world@Vector(v)for v in o.bound_box]
  if max(v.x for v in bb)<-85 or min(v.x for v in bb)>85 or max(v.y for v in bb)<-90 or min(v.y for v in bb)>90:continue
  o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in t.vertices)for t in o.data.loop_triangles)
 print('BVH',len(vs),len(fs),flush=True);return BVHTree.FromPolygons(vs,fs,all_triangles=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R554_SUR_ASINMIS_TAS_PBR_ADAY_v001.blend'));bv=tree();missing=[]
for x in range(-85,86):
 for y in range(-90,91):
  if bv.ray_cast(Vector((x+.37,y+.43,60)),Vector((0,0,-1)),140)[0]is None:missing.append([x+.37,y+.43])
del bv;print('candidate missing',len(missing),flush=True);bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));bv=tree();rows=[]
for x,y in missing:
 p=bv.ray_cast(Vector((x,y,60)),Vector((0,0,-1)),140)[0]
 if p is not None:rows.append(dict(x=x,y=y,sourceZ=p.z))
(R/'reports/R555_EXPOSED_COVERAGE_GAPS.json').write_text(json.dumps(dict(method='One metre staggered whole-ring coverage; render-hidden meshes and vegetation excluded. Mesh BVH checks only: does not certify modifiers or shape fidelity.',count=len(rows),rows=rows),indent=2));print('MISSING',len(rows),rows[:20])
