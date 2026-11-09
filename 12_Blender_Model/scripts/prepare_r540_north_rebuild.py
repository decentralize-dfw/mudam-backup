exec(open(__file__.replace('prepare_r540_north_rebuild.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
from shapely.geometry import Polygon
from shapely import constrained_delaunay_triangles
poly=json.loads((R/'reports/R328_RUIN_FLOOR_PLANES.json').read_text())['north']['outline'];line=np.array(poly[:3]);normals=[];tangents=[];capfits=[];floorControls=[]
for seg in [0,1]:
 a,b=line[seg:seg+2];t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]]);normals.append(n);tangents.append(t);s=(p[:,:2]-a)@t;o=(p[:,:2]-a)@n;length=np.linalg.norm(b-a)
 def cells(q):
  box={}
  for v in q:box.setdefault(tuple(np.floor(v[:2]/.4).astype(int)),[]).append(v)
  return np.array([np.median(v,axis=0)for v in box.values()if len(v)>1 and np.ptp(np.array(v)[:,2])<.1])
 q=cells(p[(cl==2)&(s>.6)&(s<length-.6)&(o>(3.45 if seg==0 else 2.95))&(o<(4.05 if seg==0 else 3.55))&(p[:,2]>-1.3)&(p[:,2]<.6)])
 ss=(q[:,:2]-a)@t;A=np.c_[np.ones(len(q)),ss];test=np.arange(len(q))%4==0;c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];e=A[test]@c-q[test,2];capfits.append(dict(coefficients=c.tolist(),heldout=dict(count=int(sum(test)),rms=float(np.sqrt(np.mean(e*e))),max=float(max(abs(e)))),controls=q.tolist()))
 q=cells(p[(cl==2)&(s>.6)&(s<length-.6)&(o>.75)&(o<2.25)&(p[:,2]<-2.1)&(p[:,2]>-3.3)]);floorControls.extend(q.tolist())
def offset_chain(widths):
 angle0=np.arctan2(normals[0][1],normals[0][0]);angle1=np.arctan2(normals[1][1],normals[1][0]);arc=[]
 for f in np.linspace(0,1,9):
  angle=angle0*(1-f)+angle1*f;radius=widths[0]*(1-f)+widths[1]*f;arc.append((line[1]+radius*np.array([np.cos(angle),np.sin(angle)])).tolist())
 return [(line[0]+normals[0]*widths[0]).tolist()]+arc+[(line[2]+normals[1]*widths[1]).tolist()]
inner=offset_chain([3.25,2.75]);outer=offset_chain([3.9,3.4]);z0=capfits[0]['coefficients'][0];z1=z0+capfits[0]['coefficients'][1]*np.linalg.norm(line[1]-line[0]);z2=capfits[1]['coefficients'][0];z3=z2+capfits[1]['coefficients'][1]*np.linalg.norm(line[2]-line[1]);cap=[float(z0)]+[float(z1*(1-f)+z2*f)for f in np.linspace(0,1,9)]+[float(z3)]
floor=Polygon(inner+[line[2].tolist(),line[1].tolist(),line[0].tolist()]);q=np.array(floorControls);A=np.c_[q[:,:2],np.ones(len(q))];keys=np.floor(q[:,:2]/.4).astype(int);test=(keys[:,0]+3*keys[:,1])%4==0;c=np.linalg.lstsq(A[~test],q[~test,2],rcond=None)[0];e=A[test]@c-q[test,2]
d=dict(inner=inner,outer=outer,cap=cap,capFits=capfits,floorOutline=list(floor.exterior.coords)[:-1],floorTriangles=[list(t.exterior.coords)[:3]for t in constrained_delaunay_triangles(floor).geoms],floorPlane=c.tolist(),floorHeldout=dict(count=int(sum(test)),rms=float(np.sqrt(np.mean(e*e))),max=float(max(abs(e)))),accepted=False)
(R/'reports/R540_NORTH_REBUILD_DESIGN.json').write_text(json.dumps(d,indent=2));print('CAP',cap,[f['heldout']for f in capfits]);print('FLOOR',floor.area,d['floorHeldout']);print('INNER',inner)

