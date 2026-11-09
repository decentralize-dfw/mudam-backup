from pathlib import Path
import bpy,json,numpy as np
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169'
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'))
cs=[];ns=[];areas=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 for p in o.data.polygons:
  n=o.matrix_world.to_3x3()@p.normal
  if abs(n.z)>.25:continue
  c=o.matrix_world@p.center
  cs.append(tuple(c));ns.append(tuple(n));areas.append(p.area)
c=np.array(cs);n=np.array(ns);w=np.array(areas);result=[]
for b in json.loads((R/'config/r169_building_targets.json').read_text())['buildings']:
 ring=np.array(b['rings'][0]);edges=[]
 for i,(a,z) in enumerate(zip(ring,np.roll(ring,-1,axis=0))):
  v=z-a;length=np.linalg.norm(v)
  if length<2:continue
  t=v/length;out=np.array([t[1],-t[0]]);delta=c[:,:2]-a;along=delta@t;dist=delta@out
  mask=(along>1)&(along<length-1)&(abs(dist)<4)&(c[:,2]>b['base']+2)&(c[:,2]<b['base']+9)&(abs(n[:,:2]@out)>.94)
  d=dist[mask];ww=w[mask]
  if len(d)>0:
   order=np.argsort(d);dd=d[order];weights=ww[order];median=float(dd[np.searchsorted(np.cumsum(weights),weights.sum()/2)])
   hist,bins=np.histogram(d,bins=np.arange(-4,4.05,.1),weights=ww);smooth=np.convolve(hist,np.ones(5),mode='same');peak=int(smooth.argmax());mode=float((bins[peak]+bins[peak+1])/2);coherent=abs(d-mode)<.25;support=float(ww[coherent].sum()/ww.sum());profile=[]
   for low in np.arange(b['base']+2,b['base']+9,.5):
    take=mask&(c[:,2]>=low)&(c[:,2]<low+.5);pd=dist[take];pw=w[take]
    if len(pd)<5:continue
    ph,pb=np.histogram(pd,bins=np.arange(-4,4.05,.1),weights=pw);ps=np.convolve(ph,np.ones(5),mode='same');pi=int(ps.argmax());profile.append([float(low+.25),float((pb[pi]+pb[pi+1])/2),float(pw.sum())])
   edges.append(dict(mode=mode,support=support,profile=profile,edge=i,length=float(length),samples=len(d),area=float(ww.sum()),offset=median,spread=float(np.percentile(d,90)-np.percentile(d,10))))
 result.append(dict(id=b['id'],edges=edges));print(result[-1],flush=True)
(D/'facade_plane_modes.json').write_text(json.dumps(result,indent=2))

