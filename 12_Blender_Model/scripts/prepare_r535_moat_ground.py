exec(open(__file__.replace('prepare_r535_moat_ground.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
d=json.loads((R/'reports/R534_RUIN_WALL_DESIGN.json').read_text());line=np.array(d['stations'])[:,:2];out={}
for seg in [0,5]:
 a,b=line[seg:seg+2];delta=b-a;length=np.linalg.norm(delta);t=delta/length;n=np.array([-t[1],t[0]]);s=(p[:,:2]-a)@t;o=(p[:,:2]-a)@n;q=p[(cl==2)&(s>.6)&(s<length-.6)&(o<-1.5)&(o>-2.35)&(p[:,2]<-1.2)&(p[:,2]>-4)];cells={}
 for v in q:cells.setdefault(tuple(np.floor(v[:2]/.4).astype(int)),[]).append(v)
 pts=np.array([np.median(v,axis=0)for v in cells.values()if len(v)>1 and np.ptp(np.array(v)[:,2])<.1]);out[str(seg)]=dict(controls=pts.tolist());print(seg,len(q),len(pts),np.quantile(q[:,2],[0,.5,1])if len(q)else None)
 if len(pts)>8:
  ss=(pts[:,:2]-a)@t;A=np.c_[np.ones(len(pts)),ss];test=np.arange(len(pts))%4==0;c=np.linalg.lstsq(A[~test],pts[~test,2],rcond=None)[0];e=A[test]@c-pts[test,2];out[str(seg)].update(coefficients=c.tolist(),heldout=dict(count=int(sum(test)),rms=float(np.sqrt(np.mean(e*e))),max=float(max(abs(e)))));print(out[str(seg)]['heldout'],c)
(R/'reports/R535_MOAT_GROUND.json').write_text(json.dumps(out,indent=2))

