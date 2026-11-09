exec(open(__file__.replace('prepare_r532_whole_paving.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import split
from shapely import constrained_delaunay_triangles
# Paving outline traced from R532 800px orthographic source, 50m extent.
pixels=[(-20,450),(210,370),(230,340),(350,310),(510,250),(580,200),(640,0),(730,0),(700,140),(680,250),(740,320),(680,390),(620,450),(560,515),(192,556),(192,515),(-20,490)]
poly=Polygon([(37+x/16,-23-y/16)for x,y in pixels]);q=p[(cl==2)&(p[:,0]>35)&(p[:,0]<84)&(p[:,1]>-60)&(p[:,1]<-22)];q=np.array([v for v in q if poly.buffer(-.3).contains(Point(v[:2]))]);cells={}
for v in q:cells.setdefault(tuple(np.floor(v[:2]/.5).astype(int)),[]).append(v)
q=np.array([np.median(v,axis=0)for v in cells.values()if len(v)>1 and np.ptp(np.array(v)[:,2])<.1]);q=q[q[:,2]<.052*q[:,0]-4.65+np.maximum(q[:,1]+48,0)*.12]
features=lambda q:np.c_[np.ones(len(q)),q[:,0]-60,q[:,1]+45,np.maximum(q[:,0]-58,0),np.maximum(q[:,0]-72,0),np.maximum(q[:,1]+42,0)]
A=features(q);keys=np.floor(q[:,:2]/.5).astype(int);test=(keys[:,0]+3*keys[:,1])%4==0;c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];e=A[test]@c-q[test,2]
parts=[poly]
for line in [LineString([(58,-100),(58,0)]),LineString([(72,-100),(72,0)]),LineString([(0,-42),(100,-42)])]:parts=[piece for part in parts for piece in split(part,line).geoms]
d=dict(outline=list(poly.exterior.coords)[:-1],pieces=[list(part.exterior.coords)[:-1]for part in parts],coefficients=c.tolist(),controls=q.tolist(),training=int(sum(~test)),heldout=dict(count=int(sum(test)),rms=float(np.sqrt(np.mean(e*e))),max=float(max(abs(e))),p95=float(np.quantile(abs(e),.95))),accepted=False)
(R/'reports/R532_WHOLE_PAVING_PLANES.json').write_text(json.dumps(d,indent=2));print(d['heldout'],len(q),d['coefficients'])

