import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_HENDEK_ADAY_v007.blend'))
a=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 b=[o.matrix_world@Vector(v) for v in o.bound_box]
 if min(p.x for p in b)<-161<max(p.x for p in b) and min(p.y for p in b)<-160<max(p.y for p in b):a.append([o.name,len(o.data.polygons),min(p.z for p in b),max(p.z for p in b)])
(R/'reports/R172_OVERLAY_OBJECTS.json').write_text(json.dumps(a,indent=2));print(a)
