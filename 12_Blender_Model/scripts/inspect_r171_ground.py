from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R170_KAYNAK_ADA_BORDUR_ADAY_v002.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH' and any(k in o.name.upper() for k in ['TERRAIN','GROUND','LAND','SURFACE']):
  v=[o.matrix_world@Vector(p) for p in o.bound_box];print(o.name,[round(min(p[k] for p in v),1) for k in range(3)],[round(max(p[k] for p in v),1) for k in range(3)])
