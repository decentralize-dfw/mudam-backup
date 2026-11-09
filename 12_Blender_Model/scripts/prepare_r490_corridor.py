from pathlib import Path
R=Path('12_Blender_Model');s=(R/'scripts/measure_r485_wall_sections.py').read_text().replace('[20,24,28,32,36,40]','[31,32,33,34,35,36,37,38,39]').replace('range(41)','range(5)').replace('x=y-77+j*.25','x=y-66.6+j*.4').replace('R485_WALL_SECTIONS.json','R490_CORRIDOR_FLOOR.json');(R/'scripts/measure_r490_corridor.py').write_text(s)
