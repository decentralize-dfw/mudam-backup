from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj
from scipy.spatial import cKDTree
d=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=d['xyz_luref'];cl=d['classification'];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum));tree=cKDTree(p[:,:2])

from shapely.geometry import Polygon,Point
pixels=[(382,219),(445,216),(465,222),(465,319),(382,321)]
xy=[(-120+x*220/1400,95-y*220/1400) for x,y in pixels];poly=Polygon(xy);lo=poly.bounds;q=p[(cl==2)&(p[:,0]>lo[0])&(p[:,0]<lo[2])&(p[:,1]>lo[1])&(p[:,1]<lo[3])];q=np.array([v for v in q if poly.buffer(-.5).contains(Point(v[:2]))]);keys=np.floor(q[:,:2]).astype(int);cells={}
for k,v in zip(map(tuple,keys),q):cells.setdefault(k,[]).append(v)
controls=[]
for k,values in cells.items():
 a=np.array(values)
 if len(a)>=3 and np.ptp(a[:,2])<.15:controls.append(np.median(a,axis=0))
q=np.array(controls);keys=np.floor(q[:,:2]).astype(int);test=(keys[:,0]+3*keys[:,1])%4==0;x,y=q[:,:2].T;A=np.c_[np.ones(len(q)),x,y,x*x,x*y,y*y];coef=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];err=A[test]@coef-q[test,2];check=dict(heldout=int(test.sum()),training=int((~test).sum()),rms=float(np.sqrt(np.mean(err**2))),max=float(abs(err).max()));d=dict(pixels=pixels,outline=xy,coefficients=coef.tolist(),check=check,valid=check['heldout']>=8 and check['rms']<.1 and check['max']<.25,controls=q.tolist(),method='Independent six-coefficient quadratic grading model fitted to class2 cell medians, disjoint holdout; no scan mesh transfer.');(R/'reports/R458_WEST_PLAZA_GRADE.json').write_text(json.dumps(d,indent=2));print(check,d['valid'])
