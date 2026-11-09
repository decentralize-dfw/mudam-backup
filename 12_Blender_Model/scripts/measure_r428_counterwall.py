from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum));tree=cKDTree(p[:,:2])

rows=json.loads((R/'reports/R428_FRONT_WALL_COLUMNS.json').read_text());controls=[]
for row in rows:
 ids=tree.query_ball_point(row['xy'],.55);q=p[ids];cs=cl[ids];z=q[(cs==1)&(q[:,2]>-6.4)&(q[:,2]<-5.9),2];row['crestReturnCount']=len(z)
 if len(z)>=3:
  med=float(np.median(z));row['measuredCrest']=med;row['crestSpread']=float(np.ptp(z));controls.append([*row['xy'],med])
q=np.array(controls);cells=np.floor(q[:,:2]).astype(int);test=(cells[:,0]+3*cells[:,1])%4==0;A=np.c_[q[:,:2],np.ones(len(q))];coef=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];err=A[test]@coef-q[test,2];check=dict(heldout=int(test.sum()),training=int((~test).sum()),rms=float(np.sqrt(np.mean(err**2))),max=float(abs(err).max()));print(coef,check)
for row in rows:row['proposedCrest']=float(np.dot([*row['xy'],1],coef))
report=dict(rows=rows,plane=coef.tolist(),check=check,valid=check['heldout']>=4 and check['rms']<.1 and check['max']<.25,method='Existing independent wall plan; classified crest returns near its columns in photo-identified -6.4..-5.9m crest band. Holdout by whole 1m cells; no source mesh transfer.',limits=['Top band prior is constrained by photograph and R427 measurements; not all wall face/foot geometry accepted.']);(R/'reports/R428_FRONT_COUNTERWALL_LEVELS.json').write_text(json.dumps(report,indent=2))
