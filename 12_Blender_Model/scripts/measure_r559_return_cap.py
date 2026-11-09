exec(open(__file__.replace('measure_r559_return_cap.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
rows=[]
for y in [-58,-57,-56,-55,-54,-53]:
 for cls in [1,2,6]:
  q=p[(cl==cls)&(p[:,0]>49.3)&(p[:,0]<50.5)&(abs(p[:,1]-y)<.45)&(p[:,2]>-3)&(p[:,2]<0)]
  if len(q):rows.append(dict(y=y,classification=cls,points=q.tolist()));print(y,cls,len(q),np.quantile(q[:,2],[0,.25,.5,.75,1]))
(R/'reports/R559_RETURN_CAP_LIDAR.json').write_text(json.dumps(rows,indent=2))
