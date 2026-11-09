from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R209_NOVOTEL_CATILAR_v001.blend'));out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS'] or o.name.startswith(('R191_','R192_GRADE_','R189_'))):continue
 o.data.calc_loop_triangles();tris=[]
 for t in o.data.loop_triangles:
  pts=[list(o.matrix_world@o.data.vertices[i].co) for i in t.vertices]
  if max(p[0] for p in pts)<255 or min(p[0] for p in pts)>445 or max(p[1] for p in pts)<390 or min(p[1] for p in pts)>495:continue
  tris.append(pts)
 out.append(dict(name=o.name,triangles=tris))
(R/'config/r210_ground_coverage.json').write_text(json.dumps(out));print([(r['name'],len(r['triangles'])) for r in out])
