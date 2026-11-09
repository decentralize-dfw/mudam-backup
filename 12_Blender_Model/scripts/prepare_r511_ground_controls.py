exec(open(__file__.replace('prepare_r511_ground_controls.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
q=p[(cl==2)&(p[:,0]>-95)&(p[:,0]<95)&(p[:,1]>-95)&(p[:,1]<72)];cells={}
for v in q:cells.setdefault(tuple(np.floor(v[:2]).astype(int)),[]).append(v)
controls=[]
for key,values in cells.items():
 a=np.array(values)
 if len(a)>=3 and np.ptp(a[:,2])<.18:controls.append(np.median(a,axis=0).tolist())
(R/'reports/R511_STABLE_GROUND_CONTROLS.json').write_text(json.dumps(controls));print(len(controls))
