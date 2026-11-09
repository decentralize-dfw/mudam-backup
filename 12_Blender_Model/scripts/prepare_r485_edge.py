from pathlib import Path
R=Path('12_Blender_Model');s=(R/'scripts/inspect_r484_white_edge.py').read_text().replace('MUDAM_R484_KUZEYBATI_ISTINAT_DUVARI_ADAY_v002.blend','MUDAM_R485_AVLU_SUR_ZEMIN_ADAY_v002.blend')
s=s.replace("out.append(dict(pixel=[px,py],object=o.name if h else None,position=list(loc) if h else None))","q=origin+forward*((-6-origin.z)/forward.z);vh,vp,vn,vi,vo,vm=s.ray_cast(dg,Vector((q.x,q.y,20)),Vector((0,0,-1)),distance=60);out.append(dict(pixel=[px,py],object=o.name if h else None,position=list(loc) if h else None,atFloor=list(q),verticalObject=vo.name if vh else None,verticalHit=list(vp) if vh else None))")
s=s.replace('R484_WHITE_EDGE_RAYS.json','R485_WHITE_EDGE_RAYS.json');(R/'scripts/inspect_r485_edge.py').write_text(s)
