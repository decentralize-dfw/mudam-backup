exec(open(__file__.replace('prepare_r557_planes.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
from shapely.geometry import Polygon
from shapely import contains_xy
parts=json.loads((R/'reports/R557_SOURCE_CONTROLS.json').read_text())
for q in parts:
 if q['name'].startswith(('NW_','NORTH_')):
  poly=Polygon(q['outline']);pp=p[(cl==2)&contains_xy(poly.buffer(.3),p[:,0],p[:,1])];cells={}
  for v in pp:cells.setdefault(tuple(np.floor(v[:2]/.25).astype(int)),[]).append(v)
  pts=np.array([np.median(v,axis=0)for v in cells.values()if len(v)>1 and np.ptp(np.array(v)[:,2])<.12]);q['controlSource']='Classified2024ground cells; ACT canopy excluded'
 else:pts=np.array(q['sourceControls']);q['controlSource']='ACT exposed ground controls'
 if q['name']=='WEST_APPROACH_0':pts=pts[pts[:,2]<-3.1]
 print(q['name'],len(pts),'Z',np.quantile(pts[:,2],[0,.5,1]));q['fitControls']=pts.tolist();A=np.c_[pts[:,:2],np.ones(len(pts))];test=np.arange(len(pts))%4==0;c=np.linalg.lstsq(A[~test],pts[~test,2],rcond=None)[0];e=A[test]@c-pts[test,2];q['plane']=c.tolist();q['heldoutCount']=int(sum(test));q['heldoutRMS']=float(np.sqrt(np.mean(e*e)));q['heldoutMax']=float(max(abs(e)));print(q['plane'],q['heldoutRMS'],q['heldoutMax'])
(R/'reports/R557_GROUND_PLANES.json').write_text(json.dumps(parts,indent=2))

