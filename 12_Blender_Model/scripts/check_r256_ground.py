import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R256_IKI_KULE_MIMARI_ADAY_v001.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.name not in ['R154_FAR_GROUND','R182_EXTENSION_GROUND','R152_CLASS2_TERRAIN']:continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);out={}
for name,z in [('R255_A_FLOOR',6.1),('R256_B_FLOOR',6.0)]:
 o=bpy.data.objects[name];samples=[];missing=[]
 for e in o.data.edges:
  a,b=[o.matrix_world@o.data.vertices[i].co for i in e.vertices]
  if abs(a.z-z)>.001 or abs(b.z-z)>.001:continue
  count=math.ceil((b-a).length/.5)
  for j in range(count+1):
   q=a.lerp(b,j/count);h,*_=g.ray_cast(Vector((q.x,q.y,100)),Vector((0,0,-1)),200)
   if h:samples.append(h.z)
   else:missing.append(tuple(q))
 out[name]=dict(samples=len(samples),missing=len(missing),groundMin=min(samples),groundMax=max(samples),maxGap=z-min(samples))
(R/'reports/R256_TOWERS_GROUND.json').write_text(json.dumps(out,indent=2));print(out)
