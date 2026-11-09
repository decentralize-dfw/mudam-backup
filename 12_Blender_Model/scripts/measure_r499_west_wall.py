import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();out=[]
for y in [-59,-58.5,-58,-57.5,-57,-56.5,-56,-55.5,-55,-54.5,-54,-53.5,-53,-52.5]:
 for z in [-2,-2.5,-3,-3.5,-4,-4.5,-5]:
  origin=Vector((43,y,z))
  for j in range(8):
   h,p,n,*_=s.ray_cast(dg,origin,Vector((1,0,0)),distance=10)
   if not h or p.x>53:break
   out.append(dict(y=y,z=z,position=list(p),normal=list(n)));origin=p+Vector((.01,0,0))
(R/'reports/R499_SOURCE_WEST_FACE_RAYS.json').write_text(json.dumps(out,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R497_ARAZI_YUZEY_NORMAL_ADAY_v001.blend'));out=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or ('WALL' not in ob.name and 'wall' not in ob.name):continue
 vv=[ob.matrix_world@v.co for v in ob.data.vertices];near=[list(v) for v in vv if 43<v.x<52 and -64<v.y<-51]
 if near:out.append(dict(name=ob.name,nearVertices=near[:100]))
(R/'reports/R499_EXISTING_WEST_JOINS.json').write_text(json.dumps(out,indent=2))
