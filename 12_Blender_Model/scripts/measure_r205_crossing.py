from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/bridge_full_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);r=json.loads((R/'config/r205_river_crossing.json').read_text());xy=r['footprint']
def inside(p):
 h=False
 for a,b in zip(xy,xy[1:]+xy[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:h=not h
 return h
samples=[]
for x in np.arange(min(p[0] for p in xy),max(p[0] for p in xy),.5):
 for y in np.arange(min(p[1] for p in xy),max(p[1] for p in xy),.5):
  if not inside((x,y)):continue
  h,n,*_=g.ray_cast(Vector((x,y,-65)),Vector((0,0,-1)),30)
  if h and n.z>.85:samples.append([x,y,h.z])
a=np.array(samples);origin=a[:,:2].mean(0);X=np.c_[a[:,:2]-origin,np.ones(len(a))];rng=np.random.default_rng(205);best=None
for _ in range(400):
 ix=rng.choice(len(a),3,False)
 if abs(np.linalg.det(X[ix]))<.01:continue
 c=np.linalg.solve(X[ix],a[ix,2]);mask=abs(X@c-a[:,2])<.18
 if best is None or mask.sum()>best.sum():best=mask
c=np.linalg.lstsq(X[best],a[best,2],rcond=None)[0];err=abs(X@c-a[:,2]);r.update(dict(samples=samples,origin=origin.tolist(),plane=c.tolist(),support=float((err<.2).mean()),inlier_p90=float(np.quantile(err[best],.9)),accepted=False))
(R/'config/r205_river_crossing_measured.json').write_text(json.dumps(r,indent=2));print(c,r['support'],r['inlier_p90'])
s=bpy.context.scene;t=Vector((-184,-368,-73));s.camera.location=t+Vector((-35,-50,35));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=50;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.filepath=str(R/'renders/qa/R205_road_bridge_source.png');bpy.ops.render.render(write_still=True)
