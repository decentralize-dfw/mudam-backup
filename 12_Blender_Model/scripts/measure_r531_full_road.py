exec(open(__file__.replace('measure_r531_full_road.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
q=p[(cl==2)&(p[:,0]>49)&(p[:,0]<74)&(p[:,1]>.102*p[:,0]-62.4)&(p[:,1]<.102*p[:,0]-55)]
cells={}
for v in q:cells.setdefault(tuple(np.floor(v[:2]/.5).astype(int)),[]).append(v)
pts=[]
for v in cells.values():
 a=np.array(v)
 if len(a)>1 and np.ptp(a[:,2])<.1:pts.append(np.median(a,axis=0))
q=np.array(pts);q=q[q[:,2]<.052*q[:,0]-4.9];A=np.c_[q[:,:2],np.ones(len(q))];keys=np.floor(q[:,:2]/.5).astype(int);test=(keys[:,0]+3*keys[:,1])%4==0;c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];e=A[test]@c-q[test,2]
d=dict(controls=q.tolist(),plane=c.tolist(),training=int(sum(~test)),heldout=dict(count=int(sum(test)),rms=float(np.sqrt(np.mean(e*e))),max=float(max(abs(e)))))
(R/'reports/R531_FULL_ROAD_PLANE.json').write_text(json.dumps(d,indent=2));print({k:v for k,v in d.items()if k!='controls'})
