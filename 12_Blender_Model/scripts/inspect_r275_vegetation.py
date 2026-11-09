import bpy,json
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R275_AVLU_ZEMIN_BIRLESIM_ADAY_v001.blend'));out=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and any(k in o.name.lower() for k in ['tree','canop','forest','veget','foliage']):out.append(dict(name=o.name,verts=len(o.data.vertices)))
print('VEGETATION',json.dumps(out),flush=True)
