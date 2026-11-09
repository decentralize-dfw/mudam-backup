import bpy,collections
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R250_NOVOTEL_CATIBOLMELERI_ADAY_v001.blend'));o=bpy.data.objects['R176_NOVOTEL_HIGH'];print('MATS',[(i,m.name) for i,m in enumerate(o.data.materials)],flush=True);print('FACES',collections.Counter((p.material_index,len(p.vertices),round(p.normal.z,1)) for p in o.data.polygons),flush=True)
