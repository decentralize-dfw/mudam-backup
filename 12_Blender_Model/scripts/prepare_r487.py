from pathlib import Path
R=Path('12_Blender_Model');s=(R/'scripts/measure_r481_path.py').read_text();start=s.index('pixels=');end=s.index(';poly=Polygon',start)
s=s[:start]+"pixels=[(220,571),(246,530),(449,294),(498,239),(526,248),(494,300),(480,355),(478,470),(427,521),(309,635),(268,642)];xy=[(-70+x*.075,60-y*.075) for x,y in pixels]"+s[end:]
s=s.replace("R481_WEST_PATH_GRADE.json","R487_LOWER_PASSAGE_GRADE.json").replace('poly.buffer(-.5)','poly.buffer(-.45)');(R/'scripts/measure_r487_passage.py').write_text(s)
