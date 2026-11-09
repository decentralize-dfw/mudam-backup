from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
r=[]
for x,y in [(42,-25),(42,-15),(42,0),(43,15),(45,30),(46,45),(37,-25),(38,-15),(39,0),(40,15)]:
 ids=tree.query_ball_point([x,y],.5);q=p[ids];c=cl[ids];g={}
 for k in sorted(set(c)):
  z=q[c==k,2];g[str(k)]=[len(z),float(z.min()),float(np.median(z)),float(z.max())]
 r.append(dict(xy=[x,y],classes=g))
(R/'reports/R372_EAST_MUSEUM_MOAT_LEVELS.json').write_text(json.dumps(r,indent=2));print(r)
