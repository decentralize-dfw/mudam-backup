exec(open(__file__.replace('measure_r568_cap_width.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
a,b,c=json.loads((R/'reports/R529_SOUTH_FACE_PLANE.json').read_text())['plane'];rows=[]
for x in [50,52,54,56,60,64,68]:
 yf=a*x+b*-1.6+c
 for off in np.arange(-.25,2.76,.25):
  y=yf+off
  for cls in [1,2]:
   q=p[(cl==cls)&(abs(p[:,0]-x)<.45)&(abs(p[:,1]-y)<.12)&(p[:,2]>-4)&(p[:,2]<0)]
   if len(q)>1:rows.append(dict(x=x,offset=float(off),classification=cls,y=y,n=len(q),z=np.quantile(q[:,2],[.1,.5,.9]).tolist()))
(R/'reports/R568_CAP_WIDTH_SECTIONS.json').write_text(json.dumps(rows,indent=2))
for r in rows:print(r['x'],r['offset'],r['classification'],[round(z,2)for z in r['z']])
