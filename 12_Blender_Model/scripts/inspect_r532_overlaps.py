import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R532_GUNEY_TAM_YAYA_ALANI_ADAY_v001.blend'));dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(62,-43),(65,-44),(70,-40),(42,-51),(59,-46)]:
 origin=Vector((x,y,20));hits=[]
 for k in range(7):
  hit,p,n,i,o,m=bpy.context.scene.ray_cast(dg,origin,Vector((0,0,-1)),distance=60)
  if not hit:break
  hits.append((o.name,p.z));origin=p+Vector((0,0,-.0001))
 print(x,y,hits,flush=True)
