from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]

starts=[(688,273),(660,317),(632,360),(604,404),(576,448),(548,491),(520,535),(439,671),(411,714),(383,758),(355,802),(327,846),(299,889),(271,933),(243,977),(215,1020)]
parts=[]
for i,(a,b) in enumerate(zip(starts,starts[1:])):
 dx=b[0]-a[0];dy=b[1]-a[1];end=(a[0]+dx*.77,a[1]+dy*.77);parts.append((f'bay_{i}',[a,(a[0]+212,a[1]+124),(end[0]+212,end[1]+124),end]))

for name,pixels in parts:
 if len(pixels)==3:pixels=[pixels[0],pixels[1],pixels[2],pixels[2]]
 p=np.array([[290+x/12,285-y/12] for x,y in pixels]);origin=p.mean(axis=0);samples=[]
 for a in np.linspace(.15,.85,25):
  for b in np.linspace(.15,.85,25):
   xy=(1-a)*(1-b)*p[0]+a*(1-b)*p[1]+a*b*p[2]+(1-a)*b*p[-1];h,n,*_=g.ray_cast(Vector((*xy,200)),Vector((0,0,-1)),300)
   if h and n.z>.7 and 15<h.z<30:samples.append([*(xy-origin),h.z])
 arr=np.array(samples);train=arr[::2];test=arr[1::2];A=np.c_[train[:,:2],np.ones(len(train))];mask=np.ones(len(train),bool)
 for _ in range(5):
  fit=np.linalg.lstsq(A[mask],train[mask,2],rcond=None)[0];err=abs(A@fit-train[:,2]);mask=err<max(.12,float(np.percentile(err,65)))
 e=abs(np.c_[test[:,:2],np.ones(len(test))]@fit-test[:,2]);rows.append(dict(name=name,polygon=p.tolist(),origin=origin.tolist(),plane=fit.tolist(),cornerRoofs=[float(np.dot([*(xy-origin),1],fit)) for xy in p],samples=len(arr),support=float(np.mean(e<.25)),p90=float(np.percentile(e,90))))
(R/'config/r281_roof_bays.json').write_text(json.dumps(rows,indent=2));print(rows,flush=True)
