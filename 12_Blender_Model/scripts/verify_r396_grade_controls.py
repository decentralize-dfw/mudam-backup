from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
d=json.loads((R/'reports/R396_GRADE_CONTACT.json').read_text());rows=[]
for a in d['changes']:
 ids=tree.query_ball_point((a['x'],a['y']),.35);q=p[ids];q=q[np.isin(cl[ids],[2])]
 if len(q)<3 or np.ptp(q[:,2])>.18:continue
 z=float(np.median(q[:,2]));rows.append(dict(x=a['x'],y=a['y'],z=z,before=a['old']-z,after=a['new']-z,delta=a['new']-a['old']))
before=np.array([a['before'] for a in rows]);after=np.array([a['after'] for a in rows]);out=dict(controls=len(rows),beforeRMS=float(np.sqrt(np.mean(before**2))),afterRMS=float(np.sqrt(np.mean(after**2))),maxAfter=float(abs(after).max()),worseByMoreThan10cm=sum(abs(a['after'])>abs(a['before'])+.1 for a in rows),rows=rows);(R/'reports/R396_CLASSIFIED_GRADE_CHECK.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='rows'})
