exec(open(__file__.replace('measure_r564_south_cap.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
a,b,c=json.loads((R/'reports/R529_SOUTH_FACE_PLANE.json').read_text())['plane'];rows=[]
for x in np.arange(49.5,73,.5):
 z=-2.02+min(1,max(0,(x-54)/4))*.57;yf=a*x+b*z+c
 q=p[(cl==1)&(abs(p[:,0]-x)<.24)&(p[:,1]>yf+.25)&(p[:,1]<yf+1.65)&(p[:,2]>z-.4)&(p[:,2]<z+.7)]
 if len(q)>2:rows.append(dict(x=float(x),n=len(q),z=np.quantile(q[:,2],[.1,.5,.9]).tolist()))
(R/'reports/R564_SOUTH_CAP_CELLS.json').write_text(json.dumps(rows,indent=2))
for r in rows:print(round(r['x'],2),r['n'],[round(z,3)for z in r['z']])
