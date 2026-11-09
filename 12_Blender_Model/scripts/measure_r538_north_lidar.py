exec(open(__file__.replace('measure_r538_north_lidar.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
d=json.loads((R/'reports/R538_NORTH_WALL_CAP.json').read_text());line=np.array(d['line']);rows=[]
for seg in [0,2]:
 a,b=line[seg:seg+2];t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]]);s=(p[:,:2]-a)@t;o=(p[:,:2]-a)@n
 for f in np.arange(.05,1,.1):
  rec=dict(segment=seg,t=float(f),samples=[])
  for off in [-.5,0,.5]:
   for klass in [1,2,6]:
    q=p[(cl==klass)&(abs(s-f*np.linalg.norm(b-a))<.4)&(abs(o-off)<.25)&(p[:,2]<2)]
    if len(q):rec['samples'].append(dict(offset=off,classification=klass,count=len(q),z=np.quantile(q[:,2],[.1,.5,.9]).tolist()))
  rows.append(rec)
(R/'reports/R538_NORTH_LIDAR_CAP.json').write_text(json.dumps(rows,indent=2));print(rows)
