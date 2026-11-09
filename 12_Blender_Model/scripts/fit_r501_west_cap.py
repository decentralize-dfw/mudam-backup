exec(open(__file__.replace('fit_r501_west_cap.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('rows=[]')[0])
results=[]
for k,(a,b) in enumerate(zip(line,line[1:])):
 t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]]);delta=p[:,:2]-a;s=delta@t;o=delta@n
 mask=(s>=0)&(s<=np.linalg.norm(b-a))&(abs(o)<1.3)&(cl==1);q=p[mask];ss=s[mask]
 hist,edges=np.histogram(q[:,2],bins=np.arange(-15,10,.1));mode=float((edges[hist.argmax()]+edges[hist.argmax()+1])/2)
 sel=abs(q[:,2]-mode)<.2;q=q[sel];ss=ss[sel];keys=np.floor(ss/.4).astype(int);controls=[]
 for cell in np.unique(keys):
  vals=q[keys==cell]
  if len(vals)>=3:controls.append([float(np.median(ss[keys==cell])),float(np.quantile(vals[:,2],.9))])
 controls=np.array(controls);test=np.arange(len(controls))%4==0;M=np.c_[np.ones(len(controls)),controls[:,0]];coef=np.linalg.lstsq(M[~test],controls[~test,1],rcond=None)[0];e=M[test]@coef-controls[test,1]
 results.append(dict(segment=k,start=a.tolist(),end=b.tolist(),dominantClass1Elevation=mode,controls=controls.tolist(),coefficients=coef.tolist(),training=int((~test).sum()),heldout=int(test.sum()),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),method='Dominant elevation mode in non-ground/non-vegetation class1 corridor; 0.4m station cells 90th quantile, independent linear cap grade with disjoint withheld stations. Mode derived before selection; buried bottom and wall thickness not surveyed.'))
(R/'reports/R501_WEST_WALL_CAP_FITS.json').write_text(json.dumps(results,indent=2));print([{k:v for k,v in r.items() if k!='controls'} for r in results])
