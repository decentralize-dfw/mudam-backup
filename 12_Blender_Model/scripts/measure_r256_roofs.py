import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r165/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def xy(p):return np.array([211+p[0]*.05,443-p[1]*.05])
patches=[[(640,239),(871,492),(670,674),(453,420)],[(339,505),(453,420),(670,674),(557,769)],[(680,702),(867,543),(1040,792),(855,959)],[(500,844),(680,702),(855,959),(682,1101)]];out=[]
for poly in patches:
 q=[xy(p) for p in poly];obs=[]
 for u in np.linspace(.12,.88,12):
  for v in np.linspace(.12,.88,12):
   p=(1-v)*((1-u)*q[0]+u*q[1])+v*((1-u)*q[3]+u*q[2]);h,*_=g.ray_cast(Vector((*p,150)),Vector((0,0,-1)),200)
   if h:obs.append([*p,float(h.z)])
 a=np.array(obs);A=np.c_[a[:,:2],np.ones(len(a))];keep=np.ones(len(a),bool)
 for _ in range(5):
  c=np.linalg.lstsq(A[keep],a[keep,2],rcond=None)[0];e=np.abs(A@c-a[:,2]);keep=e<max(.18,float(np.percentile(e,75)))
 out.append(dict(pixels=poly,ring=[p.tolist() for p in q],plane=c.tolist(),sampleCount=len(a),inliers=int(keep.sum()),p90=float(np.percentile(e,90)),zRange=[float(a[:,2].min()),float(a[:,2].max())]))
(R/'config/r256_tower_roof_planes.json').write_text(json.dumps(out,indent=2));print(out,flush=True)
