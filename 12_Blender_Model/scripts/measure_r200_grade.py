from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/bridge_full_reference.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);d=json.loads((R/'config/r200_bridge_alignment.json').read_text());p=np.array(d['centerline']);out=[]
for i in range(0,len(p),3):
 tangent=p[min(i+1,len(p)-1)]-p[max(0,i-1)];tangent/=np.linalg.norm(tangent);n=np.array([tangent[1],-tangent[0]])
 for offset in [-3,-1.82,0,1.82,3]:
  q=p[i]+n*offset;h,no,*_=g.ray_cast(Vector((*q,100)),Vector((0,0,-1)),300)
  if h and no.z>.8 and -52<h.z<-40:out.append([i*d['bridge_length']/(len(p)-1),offset,h.z,no.z])
a=np.array(out);c=np.polyfit(a[:,0],a[:,2],1)
for _ in range(3):
 mask=abs(np.polyval(c,a[:,0])-a[:,2])<.3;c=np.polyfit(a[mask,0],a[mask,2],1)
err=abs(np.polyval(c,a[:,0])-a[:,2]);report=dict(samples=out,grade=c.tolist(),sourceCoverage=[float(a[:,0].min()),float(a[:,0].max())],inlier_count=int((err<.3).sum()),sample_count=len(out),inlier_p90=float(np.quantile(err[err<.3],.9)),limits=['Beyond sourceCoverage profile is extrapolated; cannot claim scan verification'])
(R/'reports/R200_BRIDGE_GRADE.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='samples'})
