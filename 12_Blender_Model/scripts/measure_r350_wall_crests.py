from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
from PIL import Image,ImageDraw
im=Image.open(R/'renders/qa/R345_pavilion_source.png').convert('RGB');d=ImageDraw.Draw(im)
rows=[]
for label,px,py in [(str(i),x,y) for i,(x,y) in enumerate([(0,355),(120,479),(155,505),(181,516),(207,510),(275,454),(345,395),(414,336),(454,298)])]:
 xy=[-5.5+px*.0625,-18.75-py*.0625];ids=tree.query_ball_point(xy,.22);q=p[ids];classes=cl[ids];g={}
 for c in sorted(set(classes)):
  z=q[classes==c,2];g[str(c)]=[len(z),float(z.min()),float(np.median(z)),float(z.max())]
 rows.append(dict(name=label,xy=xy,pixel=[px,py],classes=g));d.ellipse((px-5,py-5,px+5,py+5),fill='red');d.text((px+7,py),label,fill='red')
im.save(R/'renders/qa/R350_wall_crest_samples.png');(R/'reports/R350_WALL_CREST_SAMPLES.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
