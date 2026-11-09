import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R311_ECCL_ORMAN_CEPHE_ADAY_v002.blend'));d=[]
for o in bpy.context.scene.objects:
 if o.name.startswith('ARCH_') and o.type=='MESH':d.append(dict(name=o.name,vertices=len(o.data.vertices),bounds=[list(min((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)),list(max((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3))]))
(R/'reports/R313_ROW_OBJECTS.json').write_text(json.dumps(d,indent=2))
