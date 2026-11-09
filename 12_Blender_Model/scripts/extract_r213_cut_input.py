from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R211_BUTUN_BINA_KABUKLARI_v002.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS','R168_SOURCE_JUNCTION'] or o.name.startswith('R177_ROAD_')):continue
 o.data.calc_loop_triangles();tris=[]
 for t in o.data.loop_triangles:
  pts=[list(o.matrix_world@o.data.vertices[i].co) for i in t.vertices]
  if max(p[0] for p in pts)<-40 or min(p[0] for p in pts)>45 or max(p[1] for p in pts)<360 or min(p[1] for p in pts)>460:continue
  tris.append(dict(index=t.index,points=pts))
 rows.append(dict(name=o.name,triangles=tris))
(R/'config/r213_cut_input.json').write_text(json.dumps(rows));print([(r['name'],len(r['triangles'])) for r in rows])
