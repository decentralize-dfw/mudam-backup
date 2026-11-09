exec(open(__file__.replace('measure_r558_pavilion_return.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
rows=[]
for y in [-58,-57,-56,-55,-54,-53]:
 rec=dict(y=y,sections=[])
 for x in np.arange(46,52.5,.5):
  qq=p[(cl==2)&(abs(p[:,0]-x)<.23)&(abs(p[:,1]-y)<.4)]
  if len(qq)>1:rec['sections'].append(dict(x=float(x),n=len(qq),z=np.quantile(qq[:,2],[.1,.5,.9]).tolist()))
 rows.append(rec);print(y,[(q['x'],[round(z,2)for z in q['z']])for q in rec['sections']])
(R/'reports/R558_PAVILION_RETURN_GROUND.json').write_text(json.dumps(rows,indent=2))
