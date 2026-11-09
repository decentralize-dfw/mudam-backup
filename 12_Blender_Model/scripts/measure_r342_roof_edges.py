from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
import shapely
from shapely.geometry import Polygon
fort=json.loads((R/'.local_source_cache/r154/fort.json').read_text());roofPixels=[(312,807),(280,776),(268,755),(344,709),(455,600),(538,512),(598,444),(632,380),(648,330),(643,287),(625,253),(662,222),(854,227),(887,265),(869,457),(839,490),(796,466),(748,459),(698,470),(640,503),(550,577),(440,686),(350,785)];outline=Polygon([(-74.5+x*65/1100,-1.5-y*65/1100) for x,y in roofPixels]);raisedPixels=[(730,218),(858,218),(891,262),(883,410),(787,410),(700,365),(730,340)];raised=Polygon([(-74.5+x*65/1100,-1.5-y*65/1100) for x,y in raisedPixels]);result={}
for label,poly in [('lower',outline.difference(raised.buffer(.5)).buffer(-.6)),('upper',raised.buffer(-.6)),('edge_lower',outline.buffer(.7).difference(outline.buffer(.25)).difference(raised.buffer(1))),('edge_upper',outline.buffer(.7).difference(outline.buffer(.25)).intersection(raised.buffer(1)))]:
 b=poly.bounds;keep=(p[:,0]>b[0])&(p[:,0]<b[2])&(p[:,1]>b[1])&(p[:,1]<b[3])&np.isin(cl,[1,6])&(p[:,2]>1)&(p[:,2]<3)
 q=p[keep];q=q[shapely.contains_xy(poly,q[:,0],q[:,1])];cells={}
 for pt in q:cells.setdefault(tuple(np.floor(pt[:2]/.5).astype(int)),[]).append(pt)
 controls=np.array([np.median(v,axis=0) for v in cells.values() if len(v)>=3 and np.ptp(np.array(v)[:,2])<.10]);A=np.column_stack([controls[:,:2],np.ones(len(controls))]);cc=np.floor(controls[:,:2]/.5).astype(int);test=(cc[:,0]+3*cc[:,1])%4==0;train=~test
 coef=np.linalg.lstsq(A[train],controls[train,2],rcond=None)[0]
 for _ in range(3):
  good=train&(abs(A@coef-controls[:,2])<.12);coef=np.linalg.lstsq(A[good],controls[good,2],rcond=None)[0]
 residual=A[test]@coef-controls[test,2];rms=float(np.sqrt(np.mean(residual**2)));mx=float(abs(residual).max());result[label]=dict(plane=coef.tolist(),rms=rms,maxAbsolute=mx,heldOut=int(test.sum()),training=int(good.sum()),valid=bool(rms<.08 and mx<.25),controls=controls.tolist())
result['roofOutline']=list(outline.exterior.coords)[:-1];result['raisedOutline']=list(raised.exterior.coords)[:-1];result['source']='R336 roof source view: independent architectural stepped plane outlines. Classified ACT2024 cell fits, no source mesh faces.'
(R/'reports/R342_ROOF_EDGE_PLANES.json').write_text(json.dumps(result,indent=2));print({k:{a:b for a,b in v.items() if a!='controls'} if isinstance(v,dict) else v for k,v in result.items()})
