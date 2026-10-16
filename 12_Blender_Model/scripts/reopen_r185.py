from pathlib import Path
import bpy,json,math
R=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'exports/r152_clean/r185_road9_REVIEW.glb'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();rows.append(dict(name=o.name,triangles=len(o.data.loop_triangles),degenerate=sum(t.area<1e-10 for t in o.data.loop_triangles),finite=all(math.isfinite(c) for v in o.data.vertices for c in v.co)))
report=dict(reopened=True,objects=rows,accepted=False,scope='Road9 only; full road network acceptance not implied')
(R/'reports/R185_REOPEN_v003.json').write_text(json.dumps(report,indent=2));print(report)
