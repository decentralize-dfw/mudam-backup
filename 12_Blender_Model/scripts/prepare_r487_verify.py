from pathlib import Path
R=Path('12_Blender_Model');s=(R/'scripts/inspect_r485_edge.py').read_text().replace('MUDAM_R485_AVLU_SUR_ZEMIN_ADAY_v002.blend','MUDAM_R487_KUZEYBATI_ALT_GECIT_ADAY_v001.blend').replace('R485_WHITE_EDGE_RAYS.json','R487_EDGE_RAYS.json');(R/'scripts/verify_r487_edge.py').write_text(s)
