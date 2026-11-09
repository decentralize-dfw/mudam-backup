exec(open(__file__.replace('prepare_r550_west_ground.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from shapely import contains_xy
D=json.loads((R/'reports/R523_WEST_REBUILD_DOMAINS.json').read_text());poly=unary_union([Polygon(a['outline'])for a in D['floor']]);q=p[(cl==2)&contains_xy(poly.buffer(-.15),p[:,0],p[:,1])];cells={}
for v in q:cells.setdefault(tuple(np.floor(v[:2]/.4).astype(int)),[]).append(v)
pts=np.array([np.median(v,axis=0)for v in cells.values()if len(v)>1 and np.ptp(np.array(v)[:,2])<.13]);print('area/bounds',poly.area,poly.bounds,'cells',len(pts),'z',np.quantile(pts[:,2],[0,.1,.5,.9,1]));(R/'reports/R550_GROUND_CONTROLS.json').write_text(json.dumps(pts.tolist()))
for y in np.arange(-20,3,2):
 qq=pts[(pts[:,1]>=y)&(pts[:,1]<y+2)]
 if len(qq):print(y,len(qq),np.quantile(qq[:,2],[0,.5,1]))
