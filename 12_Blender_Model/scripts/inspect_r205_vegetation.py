from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R205_ALT_YOL_KOPRUSU_v001.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and any(s in (o.name+' '+o.data.name).lower() for s in ['tree','vegetation','forest']):rows.append(dict(name=o.name,mesh=o.data.name,location=list(o.location),translation=list(o.matrix_world.translation),vertices=len(o.data.vertices),modifiers=[m.type for m in o.modifiers]))
(R/'reports/R205_VEGETATION_OBJECTS.json').write_text(json.dumps(rows,indent=2));print('COUNT',len(rows),rows[:4])
