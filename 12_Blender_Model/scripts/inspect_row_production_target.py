import bpy
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R170_KAYNAK_ADA_BORDUR_ADAY_v002.blend'))
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(p) for p in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if lo[0]<-60 and hi[0]>-100 and lo[1]<-285 and hi[1]>-315 and hi[2]>-66:print(o.name,len(o.data.polygons),lo,hi)

