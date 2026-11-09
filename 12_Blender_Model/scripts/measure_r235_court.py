from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=json.loads((R/'config/r193_fort_sw_planes.json').read_text());samples=[]
for r in rows:
 p=np.array(r['xy'])
 for a in np.linspace(.08,.88,14):
  for b in np.linspace(.08,.88,14):
   if a+b>.93:continue
   xy=p[0]+a*(p[1]-p[0])+b*(p[2]-p[0]);h,n,*_=g.ray_cast(Vector((*xy,100)),Vector((0,0,-1)),300)
   if h and n.z>.85 and -40<h.z<0:samples.append([*xy,h.z])
a=np.array(samples);origin=np.mean(a[:,:2],axis=0);x,y=((a[:,:2]-origin)/25).T;A=np.column_stack([np.ones(len(a)),x,y,x*x,x*y,y*y]);train=np.arange(len(a))%2==0;mask=train.copy()
for _ in range(6):
 fit=np.linalg.lstsq(A[mask],a[mask,2],rcond=None)[0];e=abs(A@fit-a[:,2]);mask=train&(e<max(.3,np.percentile(e[train],65)))
e=abs(A[~train]@fit-a[~train,2]);old=rows[0];prior=old['plane'][0]*(a[:,0]-old['origin'][0])+old['plane'][1]*(a[:,1]-old['origin'][1])+old['plane'][2];d=dict(samples=len(a),origin=origin.tolist(),scale=25,fit=fit.tolist(),p90=float(np.percentile(e,90)),support=float(np.mean(e<.35)),priorP90=float(np.percentile(abs(prior[~train]-a[~train,2]),90)),source='fort_reference.blend',method='Independent six-parameter smooth grade, alternating held-out samples; no source mesh transferred');(R/'config/r235_court_grade.json').write_text(json.dumps(d,indent=2));print(d)
