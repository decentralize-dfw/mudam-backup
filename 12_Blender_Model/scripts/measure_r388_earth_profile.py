from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
import shapely
from shapely.geometry import Polygon
from PIL import Image,ImageDraw
d=json.loads((R/'reports/R387_ROOF_INPUT.json').read_text());f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());outer=Polygon(f['footprint']);inner=Polygon(d['crestOutline']);pts=shapely.points(p[:,:2]);keep=shapely.contains(outer,pts)&~shapely.contains(inner.buffer(.3),pts)&np.isin(cl,[1,2,6])&(p[:,2]>1)&(p[:,2]<4.7)&(p[:,0]+p[:,1]>-110);raw=p[keep];cells=np.floor(raw[:,:2]/.5).astype(int);uniq=np.unique(cells,axis=0);q=[]
for cell in uniq:
 pp=raw[np.all(cells==cell,axis=1)]
 if len(pp)>=3 and np.ptp(pp[:,2])<.18:q.append(np.median(pp,axis=0))
q=np.array(q);points=shapely.points(q[:,:2]);di=shapely.distance(points,inner.boundary);do=shapely.distance(points,outer.boundary);u=di/(di+do);x=(q[:,0]+45)/30;y=(q[:,1]+35)/30;A=np.column_stack([np.ones(len(q)),u,u*u,u*u*u,x,y,u*x,u*y]);cc=np.floor(q[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0;c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];err=A@c-q[:,2];e=err[test]
out=dict(coef=c.tolist(),rms=float(np.sqrt(np.mean(e**2))),max=float(abs(e).max()),p95=float(np.quantile(abs(e),.95)),heldout=int(test.sum()),valid=bool(np.sqrt(np.mean(e**2))<.1 and abs(e).max()<.25),samples=q.tolist(),outline=f['footprint'],inner=d['crestOutline'],method='Analytic cubic cross-profile between corrected raised parapet and historic outer perimeter. Source surfaces not used.')
(R/'reports/R388_EARTH_PROFILE.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ['samples','outline','inner']})
im=Image.open(R/'renders/qa/R336_fort_roof_source.png').convert('RGB');dr=ImageDraw.Draw(im)
for line,col in [(f['footprint'],'yellow'),(d['crestOutline'],'red')]:
 pp=[((a+74.5)*1100/65,(-1.5-b)*1100/65) for a,b in line];dr.line(pp+[pp[0]],fill=col,width=3)
for (a,b,z),e in zip(q,err):
 px=(a+74.5)*1100/65;py=(-1.5-b)*1100/65;col='red' if abs(e)>.25 else 'lime';dr.ellipse((px-2,py-2,px+2,py+2),fill=col)
im.save(R/'renders/qa/R388_earth_profile_errors.png')
