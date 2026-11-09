exec(open(__file__.replace('measure_r539_north_moat_width.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
poly=json.loads((R/'reports/R328_RUIN_FLOOR_PLANES.json').read_text())['north']['outline'];line=np.array(poly[:3]);rows=[]
for seg in [0,1]:
 a,b=line[seg:seg+2];t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]]);s=(p[:,:2]-a)@t;o=(p[:,:2]-a)@n
 for f in [.2,.4,.6,.8]:
  rec=dict(segment=seg,t=f,sections=[])
  for off in np.arange(.25,5.26,.25):
   q=p[(cl==2)&(abs(s-f*np.linalg.norm(b-a))<.45)&(abs(o-off)<.13)]
   if len(q)>2:rec['sections'].append(dict(offset=float(off),count=len(q),z=np.quantile(q[:,2],[.1,.5,.9]).tolist()))
  rows.append(rec);print(seg,f,[(r['offset'],[round(z,2)for z in r['z']])for r in rec['sections']])
(R/'reports/R539_NORTH_MOAT_WIDTH.json').write_text(json.dumps(rows,indent=2))
