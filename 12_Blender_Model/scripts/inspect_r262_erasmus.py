import bpy
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R261_KULE_SERVIS_BOSLUKLARI_ADAY_v002.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith(('R215','R216','R217','R218','R219','R220','R221','R222','R223','R224','R225','R226','R227')):print(o.name,len(o.data.polygons),[(m.name if m else '') for m in o.data.materials])
