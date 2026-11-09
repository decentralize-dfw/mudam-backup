import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R546_BATI_HENDEK_KENAR_BUTUNLUGU_ADAY_v001.blend'));o=bpy.data.objects['R525_WEST_TERRACE_EXISTING_SLOPING_EDGES'];o.data.calc_loop_triangles();rows=[]
for t in o.data.loop_triangles:
 p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
 if min(v.z for v in p)>-10:rows.append([[v.x,v.y]for v in p])
(R/'reports/R548_SLOPE_FOOTPRINT.json').write_text(json.dumps(rows))
