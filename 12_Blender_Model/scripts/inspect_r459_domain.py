import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R458_BATI_SERVIS_AVLU_KOTU_ADAY_v001.blend'));o=bpy.data.objects['R152_FORECOURT_0'];o.data.calc_loop_triangles();vs=[tuple(o.matrix_world@v.co) for v in o.data.vertices];(R/'reports/R459_REMAINDER_DOMAIN.json').write_text(json.dumps(dict(vertices=vs,triangles=[list(t.vertices) for t in o.data.loop_triangles])))
