import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
def tree(path,prefix=None):
 bpy.ops.wm.open_mainfile(filepath=str(path));vs=[];fs=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or (prefix and not o.name.startswith(prefix)):continue
  o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
 return BVHTree.FromPolygons(vs,fs,all_triangles=True)
old=tree(R/'scenes/MUDAM_R284_DOGU_UZUN_CATI_ADAY_v001.blend','R284_');new=tree(R/'scenes/MUDAM_R286_DOGU_BUTUN_CATI_KESIT_ADAY_v001.blend','R286_');src=tree(R/'.local_source_cache/r166/source.blend');a=Vector((290+688/12,285-273/12));b=Vector((290+215/12,285-1020/12));w=Vector((212/12,-124/12));rows=[]
for j in range(207):
 t=(j+.371)/207
 for u in [.11,.31,.51,.71,.91]:
  p=a+(b-a)*t+w*u;ray=Vector((p.x,p.y,150));h,n,*_=src.ray_cast(ray,Vector((0,0,-1)),200);o,*_=old.ray_cast(ray,Vector((0,0,-1)),200);q,*_=new.ray_cast(ray,Vector((0,0,-1)),200)
  if h and o and q:rows.append(dict(distance=t*(b-a).length,cross=u,source=h.z,old=o.z,new=q.z,normal=n.z))
summary={}
for name in ['old','new']:
 e=np.array([abs(r[name]-r['source']) for r in rows]);summary[name]=dict(samples=len(rows),median=float(np.median(e)),p90=float(np.percentile(e,90)),within25cm=float(np.mean(e<.25)),max=float(max(e)))
(R/'reports/R286_SOURCE_COMPARISON.json').write_text(json.dumps(dict(summary=summary,samples=rows,method='Independent 207x5 reference rays; sample offsets differ from profile fit. Includes equipment and source artifacts, no exclusions.'),indent=2));print(summary,flush=True)
