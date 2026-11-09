import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R536_DOGU_KALINTI_HENDEK_TABANI_ADAY_v001.blend'));o=bpy.data.objects['R152_RUIN_PARTITION_00'];vs=[list(v.co)for v in o.data.vertices];print(vs,flush=True);(R/'reports/R537_NORTH_WALL_EXISTING.json').write_text(json.dumps(dict(vertices=vs,faces=[list(f.vertices)for f in o.data.polygons]),indent=2))
