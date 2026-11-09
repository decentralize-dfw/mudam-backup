exec(open(__file__.replace('measure_r527_south_paving.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
q=p[(cl==2)&(p[:,0]>49)&(p[:,0]<74)&(p[:,1]>.095758482712*p[:,0]-63.55)&(p[:,1]<.095758482712*p[:,0]-58.5)];cells={}
for v in q:cells.setdefault(tuple(np.floor(v[:2]/.5).astype(int)),[]).append(v)
controls=[]
for vs in cells.values():
 a=np.array(vs)
 if len(a)>=2 and np.ptp(a[:,2])<.1:controls.append(np.median(a,axis=0))
q=np.array(controls);keys=np.floor(q[:,:2]/.5).astype(int);test=(keys[:,0]+3*keys[:,1])%4==0;A=np.c_[q[:,:2],np.ones(len(q))];c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];e=A[test]@c-q[test,2];data=dict(controls=q.tolist(),plane=c.tolist(),training=int(sum(~test)),heldout=int(sum(test)),rms=float(np.sqrt(np.mean(e*e))),max=float(max(abs(e))));(R/'reports/R527_SOUTH_PAVING_PLANE.json').write_text(json.dumps(data,indent=2));print({k:v for k,v in data.items()if k!='controls'});print('RANGE',np.quantile(q[:,2],[0,.1,.5,.9,1]))
