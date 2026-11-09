from pathlib import Path
R=Path('12_Blender_Model');s=(R/'scripts/measure_r485_wall_sections.py').read_text().replace('[20,24,28,32,36,40]','[32,36,40,44]').replace('range(41)','range(19)').replace('x=y-77+j*.25','x=y-69+j*.5').replace('R485_WALL_SECTIONS.json','R490_NORTH_PASSAGE_SECTIONS.json');(R/'scripts/measure_r490_sections.py').write_text(s)
