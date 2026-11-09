import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R378_DOGU_UZUN_HENDEK_ZEMIN_ADAY_v001.blend'));o=bpy.data.objects['R35_WALL_51946353_00_0'];pts=[list(o.matrix_world@v.co) for v in o.data.vertices if abs((o.matrix_world@v.co).z+.8)<.01];(R/'reports/R380_HISTORIC_WALL_TOP_POINTS.json').write_text(json.dumps(pts));print(pts)
