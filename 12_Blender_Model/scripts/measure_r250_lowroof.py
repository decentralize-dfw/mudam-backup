import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
paths=[[(450,358),(689,712),(727,685),(493,333)],[(493,333),(468,300),(436,316)],[(507,446),(331,564)],[(578,550),(319,710),(345,758),(384,794),(436,767)],[(624,622),(463,725)],[(681,712),(628,748),(688,850),(556,942),(473,813)],[(470,813),(362,863),(405,922),(498,874)],[(566,405),(740,289),(803,379),(626,497)],[(635,514),(809,397),(883,501),(713,615)],[(879,501),(914,550),(756,659)],[(800,376),(866,440),(926,399)],[(865,226),(946,345),(1026,289)]]
out=[]
for i,pix in enumerate(paths):
 pts=[Vector((362.5+.05*x,467.5-.05*y)) for x,y in pix];zs=[]
 for a,b in zip(pts,pts[1:]):
  for t in np.linspace(.05,.95,max(5,int((b-a).length*4))):
   q=a.lerp(b,float(t));h,n,*_=g.ray_cast(Vector((q.x,q.y,80)),Vector((0,0,-1)),120)
   if h and 16.4<h.z<19 and n.z>.3:zs.append(h.z)
 out.append(dict(id=i,pixels=pix,path=[list(p) for p in pts],top=float(np.median(zs)) if zs else None,samples=len(zs),p10=float(np.quantile(zs,.1)) if zs else None,p90=float(np.quantile(zs,.9)) if zs else None,width=.45))
(R/'config/r250_lowroof_architecture.json').write_text(json.dumps(out,indent=2));print([(x['id'],x['top'],x['samples']) for x in out],flush=True)
