from pathlib import Path
R=Path('12_Blender_Model');s=(R/'scripts/measure_r494_face.py').read_text();a=s.index('for px,py in ');b=s.index(':\n origin=',a);s=s[:a]+'for px,py in [(410,510),(430,515),(450,521),(470,527),(490,533),(510,539),(530,545),(550,551),(570,557)]'+s[b:];s=s.replace('R494_VISIBLE_WALL_FACE.json','R494_VISIBLE_WALL_CREST.json');(R/'scripts/measure_r494_crest.py').write_text(s)
