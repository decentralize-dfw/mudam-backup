from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
result={}
for name,pixels,convert in [('north',[(225,413),(765,97),(798,119),(1085,628)],lambda a:(-57+a[0]*44/1200,84.5-a[1]*44/1200)),('east',[(402,-15),(904,155),(927,201),(683,725)],lambda a:(39+a[0]*42/1200,-14.25-a[1]*42/1200))]:
 path=np.array([convert(a) for a in pixels]);segments=[]
 for a,b in zip(path,path[1:]):
  d=b-a;length=np.linalg.norm(d);axis=d/length;normal=np.array([-axis[1],axis[0]]);center=(a+b)/2;ids=tree.query_ball_point(center,length/2+1);q=p[ids];classes=cl[ids];u=(q[:,:2]-a)@axis;v=(q[:,:2]-a)@normal
  keep=(u>.1)&(u<length-.1)&(abs(v)<.45)&np.isin(classes,[1,2,6])&(q[:,2]>-2)&(q[:,2]<5);q=q[keep];u=u[keep];cells={}
  for t,pt in zip(u,q):cells.setdefault(int(t/.5),[]).append([t,pt[2]])
  controls=np.array([np.median(values,axis=0) for values in cells.values() if len(values)>=3 and np.ptp(np.array(values)[:,1])<.18]);print(name,'segment',a.tolist(),'points',len(q),'bins',[(k,len(v),round(min(x[1] for x in v),2),round(max(x[1] for x in v),2)) for k,v in list(cells.items())[:6]])
  if len(controls)<8:segments.append(dict(a=a.tolist(),b=b.tolist(),valid=False,count=len(controls)));continue
  A=np.column_stack([controls[:,0],np.ones(len(controls))]);test=np.arange(len(controls))%4==0;coef=np.linalg.lstsq(A[~test],controls[~test,1],rcond=None)[0];res=A[test]@coef-controls[test,1]
  segments.append(dict(a=a.tolist(),b=b.tolist(),valid=bool(np.sqrt(np.mean(res**2))<.10 and abs(res).max()<.25),count=len(controls),zStart=float(coef[1]),zEnd=float(coef[0]*length+coef[1]),rms=float(np.sqrt(np.mean(res**2))),maxAbsolute=float(abs(res).max()),controls=controls.tolist()))
 result[name]=segments
(R/'reports/R333_OUTER_WALL_PROFILES.json').write_text(json.dumps(result,indent=2));print({k:[{a:b for a,b in v.items() if a!='controls'} for v in arr] for k,arr in result.items()})
