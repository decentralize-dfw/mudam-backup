from pathlib import Path
import bpy,numpy as np
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v066.blend'));o=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];a=o.data.color_attributes['ACT_SURFACE_COLOR']
for d in a.data:
 c=np.array(d.color[:3]);c=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4);d.color=(*c,1)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v067.blend'),compress=True)
