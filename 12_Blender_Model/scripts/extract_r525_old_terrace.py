import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R515_GUNEY_HENDEK_ALT_ZEMIN_ADAY_v001.blend'));o=bpy.data.objects['R322_WEST_MUSEUM_TERRACE'];o.data.calc_loop_triangles();(R/'reports/R525_ORIGINAL_TERRACE_MESH.json').write_text(json.dumps(dict(vertices=[list(o.matrix_world@v.co)for v in o.data.vertices],triangles=[list(t.vertices)for t in o.data.loop_triangles])));print(len(o.data.vertices),len(o.data.loop_triangles))
