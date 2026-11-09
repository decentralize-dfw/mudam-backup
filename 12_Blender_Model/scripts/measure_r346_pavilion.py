from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
from PIL import Image,ImageDraw
im=Image.open(R/'renders/qa/R345_pavilion_source.png').convert('RGB');d=ImageDraw.Draw(im)
rows=[]
for label,px,py in [('moatSW',110,385),('moatCorner',182,461),('moatNE',325,346),('innerCrest',287,345),('outerCrest',310,397),('pavilionWest',370,455),('pavilionSouth',530,550),('pavilionEast',755,388),('eastLower',820,235),('southPath',600,590)]:
 xy=[-5.5+px*.0625,-18.75-py*.0625];ids=tree.query_ball_point(xy,.5);q=p[ids];classes=cl[ids];g={}
 for c in sorted(set(classes)):
  z=q[classes==c,2];g[str(c)]=[len(z),float(z.min()),float(np.median(z)),float(z.max())]
 rows.append(dict(name=label,xy=xy,pixel=[px,py],classes=g));d.ellipse((px-5,py-5,px+5,py+5),fill='red');d.text((px+7,py),label,fill='red')
im.save(R/'renders/qa/R346_pavilion_samples.png');(R/'reports/R346_PAVILION_SAMPLES.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
