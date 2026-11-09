exec(compile(open(__file__.replace('prepare_r328_ruin_floor_planes','measure_r328_independent_lidar')).read(),__file__,'exec'))
from shapely.geometry import Polygon
reports={}
for label,file,convert in [('north','R326_NORTH_RUIN_PLAN.json',lambda a:(-57+a[0]*44/1200,84.5-a[1]*44/1200)),('east','R327_EAST_RUIN_PLAN.json',lambda a:(39+a[0]*42/1200,-14.25-a[1]*42/1200))]:
 report=json.loads((R/'reports'/file).read_text());outline=[convert(a) for a in report['outline']];holes=[Polygon([convert(a) for a in h]) for h in report['recesses']];controls=[]
 # Separate floor returns from masonry/vegetation using classification and
 # robust clusters. Fit one architectural plane, not a triangulated cloud.
 for i,h in enumerate(holes[:4]):
  inner=h.buffer(-.25)
  ids=tree.query_ball_point((h.centroid.x,h.centroid.y),max(h.bounds[2]-h.bounds[0],h.bounds[3]-h.bounds[1]))
  q=p[ids];classes=cl[ids]
  import shapely
  keep=shapely.contains_xy(inner,q[:,0],q[:,1]) & np.isin(classes,[1,2]) & (q[:,2]<-1.8)&(q[:,2]>-3.6)
  q=q[keep]
  # Spatial cell medians prevent high-density patches dominating the fit.
  cells={}
  for point in q:
   key=tuple(np.floor(point[:2]/.75).astype(int));cells.setdefault(key,[]).append(point)
  for key,values in cells.items():
   values=np.array(values)
   if len(values)>=3 and np.ptp(values[:,2])<.25:controls.append(np.median(values,axis=0).tolist())
 controls=np.array(controls);assert len(controls)>10,(label,len(controls))
 A=np.column_stack([controls[:,:2],np.ones(len(controls))]);cells=np.floor(controls[:,:2]/.75).astype(int);validation=(cells[:,0]+3*cells[:,1])%4==0;training=~validation
 coef=np.linalg.lstsq(A[training],controls[training,2],rcond=None)[0];res=controls[:,2]-A@coef
 keep=training&(np.abs(res)<.2);coef=np.linalg.lstsq(A[keep],controls[keep,2],rcond=None)[0];res=controls[keep,2]-A[keep]@coef
 test=controls[validation,2]-A[validation]@coef
 reports[label]=dict(outline=outline,plane=coef.tolist(),retainedCellCount=int(keep.sum()),rejectedCellCount=int((~keep).sum()),maxResidual=float(np.max(np.abs(res))),rmsResidual=float(np.sqrt(np.mean(res**2))),controls=controls[keep].tolist(),method='Independent architectural plane fitted to classified LiDAR floor clusters inside source-traced chambers. No scan topology transferred.',limits='Class1 is unclassified; spatial cluster and height filters used. Central recess excluded; separate depth remains unresolved.')
 reports[label]['heldOutCells']=dict(count=int(validation.sum()),rms=float(np.sqrt(np.mean(test**2))),maxAbsolute=float(np.max(np.abs(test))),usedInFit=False)
(R/'reports/R328_RUIN_FLOOR_PLANES.json').write_text(json.dumps(reports,indent=2));print('FLOOR_PLANES',[(k,v['retainedCellCount'],v['rmsResidual'],v['maxResidual']) for k,v in reports.items()])
