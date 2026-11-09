from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
pixels=[(255,642),(1065,468),(1140,733),(325,907)];q=np.array([[-80+(x-700)/25,-301+(700-y)/25] for x,y in pixels]);records=[]
for k in range(4):
 a=q[k];b=q[(k+1)%4];t=b-a;t/=np.linalg.norm(t);n=np.array([-t[1],t[0]]);hits=[]
 for u in np.linspace(.08,.92,35):
  p=a*(1-u)+b*u
  for z in np.linspace(-72,-66.3,25):
   start=Vector((*list(p+n*2),z));h,norm,idx,dist=tree.ray_cast(start,Vector((*list(-n),0)),4)
   if h and abs(norm.z)<.5 and abs(norm.x*n[0]+norm.y*n[1])>.8:hits.append([u,z,2-dist,*h])
 offsets=np.array([h[2] for h in hits]);hist,edges=np.histogram(offsets,bins=np.arange(-2,2.051,.1));peak=(edges[np.argmax(hist)]+edges[np.argmax(hist)+1])/2;cluster=[h for h in hits if abs(h[2]-peak)<.20];offset=float(np.median([h[2] for h in cluster])) if cluster else None
 records.append(dict(side=k,normal=n.tolist(),hits=len(hits),support=len(cluster),offset=offset,samples=hits));print(k,len(hits),len(cluster),offset)
(D/'facade_planes_v062.json').write_text(json.dumps(dict(q=q.tolist(),sides=records)))

