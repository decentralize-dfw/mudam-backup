import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model/scenes/MUDAM_R240_KALE_KALINTI_CEVRE_ZEMIN_ADAY_v001.blend')
for xy in [(-237,-196),(-228,-201),(-222,-197)]:
 deps=bpy.context.evaluated_depsgraph_get();p=Vector((*xy,0));result=[]
 for i in range(8):
  hit,loc,n,idx,o,m=bpy.context.scene.ray_cast(deps,p,Vector((0,0,-1)),distance=100)
  if not hit:break
  result.append((o.name,round(loc.z,3)));p=loc+Vector((0,0,-.02))
 print('STACK',xy,result)
