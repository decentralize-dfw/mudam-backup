exec(open(__file__.replace('measure_r515_south_moat_floor.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
cx,cy=-57.076460370468,-63.11257545086857;dx=p[:,0]-cx;dy=p[:,1]-cy;rad=np.hypot(dx,dy);front=-.7875911059732454*dx-.6161982228080831*dy;q=p[(cl==2)&(rad>5.0)&(rad<6.5)&(front>0)&(p[:,2]<-7)];cells={}
for v in q:cells.setdefault(tuple(np.floor(v[:2]/.35).astype(int)),[]).append(v)
controls=[]
for k,vs in cells.items():
 a=np.array(vs)
 if len(a)>=2 and np.ptp(a[:,2])<.1:controls.append(np.median(a,axis=0))
q=np.array(controls);keys=np.floor(q[:,:2]/.35).astype(int);test=(keys[:,0]+3*keys[:,1])%4==0;M=np.c_[np.ones(len(q)),q[:,0]-cx,q[:,1]-cy];coef=np.linalg.lstsq(M[~test],q[~test,2],rcond=None)[0];e=M[test]@coef-q[test,2];d=dict(center=[cx,cy],coefficients=coef.tolist(),controls=q.tolist(),training=int((~test).sum()),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),method='Independent plane fitted to stable class2 moat-floor cells outside southern bastion, not source mesh.');(R/'reports/R515_SOUTH_MOAT_FLOOR_PLANE.json').write_text(json.dumps(d,indent=2));print({k:v for k,v in d.items() if k!='controls'})
