from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
scene=json.loads((R/'11_Blender_Modelleme_Plani/is_paketleri.json').read_text())['latest_scene'];bpy.ops.wm.open_mainfile(filepath=str(R/scene))
rows=[]
for name in ['R05_ROUND_RAIL_INNER','R05_ROUND_RAIL_OUTER']+[f'R05_GROUND_EDGE_TOP_RAIL_{i}' for i in range(4)]:
 ob=bpy.data.objects[name];p=[ob.matrix_world@v.co for v in ob.data.vertices];rings=[sum(p[i:i+20],Vector())/20 for i in range(0,len(p),20)]
 rows.append(dict(name=name,ring_count=len(rings),start=list(rings[0]),end=list(rings[-1]),first_tangent=list((rings[1]-rings[0]).normalized()),last_tangent=list((rings[-1]-rings[-2]).normalized())))
matches=[]
for rail in rows[:2]:
 for ground in rows[2:]:
  for end in ['start','end']:
   distance=(Vector(rail['end'])-Vector(ground[end])).length
   if distance<.5:matches.append(dict(rail=rail['name'],ground=ground['name'],ground_end=end,endpoint_distance_m=distance))
report=dict(file=scene,rows=rows,matches=matches);(B/'reports/R48_rail_join_diagnosis.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
