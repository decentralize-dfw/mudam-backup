from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'));rows=[]
for y in [-28,-25,-20,-15,-10,-5,0,5,10,15,20]:
 x=32.525+.094*(y+29.1);ids=tree.query_ball_point([x,y],.3);q=p[ids];c=cl[ids];groups={}
 for k in sorted(set(c)):
  z=q[c==k,2];groups[str(k)]=[len(z),float(z.min()),float(np.median(z)),float(z.max())]
 rows.append(dict(xy=[x,y],classes=groups))
(R/'reports/R381_HISTORIC_CREST_CHECK.json').write_text(json.dumps(rows,indent=2));print(rows)
