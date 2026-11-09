from pathlib import Path
R=Path('12_Blender_Model');s=(R/'scripts/build_r484_wall_v002.py').read_text()
s=s.replace('MUDAM_R482_AVLU_YOL_SEV_BIRLESIM_ADAY_v002.blend','MUDAM_R485_AVLU_SUR_ZEMIN_ADAY_v001.blend')
s=s.replace("vs.extend([(a.x,a.y,-7.5),(b.x,b.y,-7.5),(b.x,b.y,crest(b.y)),(a.x,a.y,crest(a.y))])","vs.extend([(y-73.8,y,-7.5),(y-68.6,y,-7.5),(y-68.6,y,crest(y)),(y-71.0,y,crest(y))])")
s=s.replace('R484_NW_HISTORIC_RETAINING_WALL','R485_NW_HISTORIC_RETAINING_WALL').replace('MUDAM_R484_KUZEYBATI_ISTINAT_DUVARI_ADAY_v002.blend','MUDAM_R485_AVLU_SUR_ZEMIN_ADAY_v002.blend').replace('R484_v002_WALL_BUILD.json','R485_WALL_BUILD.json').replace('R484_v002_northwest_oblique.png','R485_northwest_oblique.png')
s=s.replace('Axis/width photographic estimates;11 held-out crest points max.0612m.','Crest piecewise fit heldout max.08344m. Face/batter source-section interpretation remains provisional; not a survey.')
(R/'scripts/build_r485_wall.py').write_text(s)
