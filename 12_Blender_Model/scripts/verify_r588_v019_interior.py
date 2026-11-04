import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];W=R/'reports'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v019.blend'));o=bpy.data.objects['R322_WEST_MUSEUM_TERRACE'];m=o.data;m.calc_loop_triangles();bv=BVHTree.FromPolygons([v.co for v in m.vertices],[tr.vertices for tr in m.loop_triangles],all_triangles=True)
a=np.array([-12.414369583129883,7.20503568649292]);b=np.array([-2.4570999145507812,-.0714000016450882]);L=np.linalg.norm(b-a);t=(b-a)/L;n=np.array([-t[1],t[0]]);za=-3.3628203868865967;zb=-3.295886516571045;k=-.009073805468898228
rows=[]
for s in np.linspace(.02,L-.02,47):
 for d in [.0002,.005,.01,.025,.05,.1,.3,.5,1.0]:
  xy=a+t*s-n*d;p,nn,i,dd=bv.ray_cast(Vector((*xy,0)),Vector((0,0,-1)),20);target=za+(zb-za)*s/L+k*d
  rows.append(dict(station=float(s),outward=d,z=None if p is None else p.z,target=float(target),error=None if p is None else p.z-target))
report=dict(scene='v019',samples=len(rows),missing=sum(r['error']is None for r in rows),maxError=max(abs(r['error'])for r in rows if r['error']is not None),RMS=float(np.sqrt(np.mean([r['error']**2 for r in rows if r['error']is not None]))),rows=rows)
(W/'R588_V019_INTERIOR_PLANE_CHECK.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k!='rows'})
assert report['missing']==0 and report['maxError']<.002
