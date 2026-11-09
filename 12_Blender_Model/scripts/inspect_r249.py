import bpy,json
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R247_ERASMUS_AVLU_SALON_ADAY_v001.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and (o.name.startswith(('R171_','R174_','R182_')) or 'GROUND' in o.name):rows.append([o.name,len(o.data.vertices)])
(R/'reports/R249_inventory.json').write_text(json.dumps(rows));print(rows,flush=True)
