from pathlib import Path
import bpy,json,math,numpy as np
from mathutils import Vector
from mathutils.geometry import convex_hull_2d
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'roof_planes_164179202.json').read_text());p=np.array(d['points']);pl=d['planes'][3];subset=p[pl['indices']];ids=convex_hull_2d([Vector((x,y)) for x,y,z in subset]);hull=subset[ids,:2];ang=float(np.load(D/'164179202.npz')['angle']);cs,sn=math.cos(ang),math.sin(ang)
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in f.vertices] for f in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);samples=[]
for x in np.arange(hull[:,0].min()+.1,hull[:,0].max(),.2):
 for y in np.arange(hull[:,1].min()+.1,hull[:,1].max(),.2):
  cr=[(b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]) for a,b in zip(hull,np.roll(hull,-1,axis=0))]
  if min(cr)<0 and max(cr)>0:continue
  wx,wy=cs*x-sn*y,sn*x+cs*y;hit,*_=tree.ray_cast(Vector((wx,wy,50)),Vector((0,0,-1)),200)
  if hit is not None:samples.append(float(hit.z-(pl['coeff'][0]*x+pl['coeff'][1]*y+pl['coeff'][2])))
r=dict(hull_local=hull.tolist(),plane=pl['coeff'],source_inliers=pl['count'],independent_samples=len(samples),residual_p50_p90_p95=np.percentile(np.abs(samples),[50,90,95]).tolist(),within_020=float(np.mean(np.abs(samples)<.2)),accepted=False)
(D/'row_fourth_slope_domain.json').write_text(json.dumps(r,indent=2));print('FOURTH_DOMAIN',r,flush=True)
